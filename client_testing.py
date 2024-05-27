import socketio
import requests
import time
# standard Python

session = requests.session()
session.proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

sio = socketio.SimpleClient(http_session = session)

connected = False
while not connected:
    try:
        sio.connect("http://obczrz5yyo5dpetitjkskk65fbcu2tqnavywz5efupvnnlpcm7etcfid.onion",  wait_timeout = 10)
        print("Socket established")
        connected = True
    except Exception as ex:
        print("Failed to establish initial connnection to server:", type(ex).__name__)
        time.sleep(2)

print('my sid is', sio.transport)
sio.emit('my message', {'foo': 'bar'})

event = sio.receive()
print(f'received event: "{event[0]}" with arguments {event[1:]}')

"""
from websocket  import  create_connection
import websocket


ws = create_connection("ws://d5u5znhpcpdgakwp4rtm7b3iukndwy7wv2opuchwn4e735ftk7oaseqd.onion",
  http_proxy_host="127.0.0.1", http_proxy_port="9050",  proxy_type="socks5h")

ws.close()

"""
