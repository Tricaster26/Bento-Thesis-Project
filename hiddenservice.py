import os
import shutil
from io import BytesIO
import stem.process
import socket
import struct
import json
import zlib
import requests
import socks

from stem.control import Controller
from flask import Flask, request, jsonify, make_response, render_template
from bento.client.api import ClientConnection
from flask_socketio import SocketIO, emit, send


app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def main():
        return "<H1> Welcome to my Bento Server!  Use /open for a given token to send an execution request</H1>"

@app.route('/open', methods=['POST'])
def exec_open_req():

    """
    Sends execute request for a token with a given call and then sends
    an open request once complete to be sent back to bento client.
    """

    sock_hs = ClientConnection('127.0.0.1', 8888) #make sure port matches
    data=request.get_data()
    jsonified = json.loads(data.decode('utf-8'))
    call = jsonified['1']
    token = jsonified['0']
    session_id, errmsg= sock_hs.send_execute_request(call, token) #every function will be executed so it is okay to always have this
    sock_hs.send_open_request(session_id) # not every time will a functino need a open request. This is a client option
    data, msg_type= sock_hs.recv_output()
    response = make_response(bytes(data))

    return response, 200

@app.route('/exec', methods=['POST'])
def exec_req():
    """
    Only sends and execute request for a token and call
    """
    sock_hs = ClientConnection('127.0.0.1', 8888) #make sure port matches
    data=request.get_data()
    jsonified = json.loads(data.decode('utf-8'))
    call = jsonified['1']
    token = jsonified['0']
    response= sock_hs.send_execute_request(call, token)
    response = make_response((response))
    return response, 200

@app.route('/store', methods=['POST'])
def store_req():
    """
    Function stores code and call, then returns the token back to client
    """
    sock_hs = ClientConnection('127.0.0.1', 8888) #make sure port matches
    data=request.get_data()
    jsonified = json.loads(data.decode('utf-8'))
    code = jsonified['1']
    name = jsonified['0']
    response= sock_hs.send_store_request(name, code)
    response = make_response((response))
    return response, 200

@app.route('/loop', methods=['POST'])
def loop_req():
    """
    Called to execute a function and let it run on the server for a longer period of time
    """
    sock_hs = ClientConnection('127.0.0.1', 8888) #make sure port matches
    data=request.get_data()
    jsonified = json.loads(data.decode('utf-8'))
    call = jsonified['1']
    token = jsonified['0']
    session_id, errmsg= sock_hs.send_execute_request(call, token) #every function will be executed so it is okay to always have this
    sock_hs.send_open_request(session_id) # not every time will a functino need a open request. This is a client option
    data_coll = []
    checker = True
    while checker:
        data, msg_type= sock_hs.recv_output()
        data_coll.append(data)
        checker = data[-1]

    return data_coll, 200

@app.route('/register', methods=['POST'])
def register_req():
    """
    Registers function to Bento Function Directory to be called by other users.
    Currently doesnt do anything, as there is no Bento function directory
    """
    sock_hs = ClientConnection('127.0.0.1', 8888)
    data=request.get_data()
    jsonified = json.loads(data.decode('utf-8'))
    token = jsonified['0']
    data = sock_hs.send_registry_request(token)

    return data, 200


print(' * Launching tor')

print(' * Connecting to tor')

with Controller.from_port() as controller:
  controller.authenticate()

  # All hidden services have a directory on disk. Lets put ours in tor's data
  # directory.

  hidden_service_dir = os.path.join(controller.get_conf('DataDirectory', '/tmp'), 'hello_world')

  # Create a hidden service where visitors of port 80 get redirected to local
  # port 5000 (this is where Flask runs by default).

  print(" * Creating our hidden service in %s" % hidden_service_dir)
  result = controller.create_hidden_service(hidden_service_dir, 80, target_port = 5000)

  # The hostname is only available when we can read the hidden service
  # directory. This requires us to be running with the same user as tor.

  if result.hostname:
    print(" * Our service is available at %s, press ctrl+c to quit" % result.hostname)
  else:
    print(" * Unable to determine our service's hostname, probably due to being unable to read the hidden service directory")
  global hostname
  hostname = result.hostname
  try:
    app.run(host='127.0.0.1', port=5000)
  finally:
    # Shut down the hidden service and clean it off disk. Note that you *don't*
    # want to delete the hidden service directory if you'd like to have this
    # same *.onion address in the future.

    print(" * Shutting down our hidden service")
    controller.remove_hidden_service(hidden_service_dir)
    shutil.rmtree(hidden_service_dir)
