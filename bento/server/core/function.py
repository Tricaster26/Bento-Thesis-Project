"""
Create and retrieve Bento functions
"""

import json
import os
import socks

from .config import opts

def get_function(token):
    """
    retrieve function from storage medium corresponding to the token
    """
    filename= f'{opts.functions_dir}/{token}.json'
    if os.path.exists(filename):
        with open(filename) as filein:
            function= json.load(filein)
        return function
    else:
        return None

def create_function(token, name, code):
    """
    write function data to storage medium based on the token
    """
    function= {'name': name, 'code': code}
    filename= f'{opts.functions_dir}/{token}.json'
    with open(filename, 'w') as outfile:
        json.dump(function, outfile)

def register_function(token, onion):
    """
    Registers function data with hidden service. Cuurently no bento Directory
    exsiting, so tokens just saved locally
    """
    function_data = get_function(token)
    key = opts.key
    token_data = {'token':token ,'onion': onion, 'function_name':function_data['name'], 'function_code':function_data['code'], 'req_type':1, 'key':key}

    socks_dir = socks.socksocket()
    socks_dir.setproxy(socks.PROXY_TYPE_SOCKS5,"127.0.0.1", 9050, True) #9050 is the default Tor proxy can be changed to user preferenance
    socks_dir.connect(("Bento_function_directory_IP", 8080)) # location of Bento function Directory to be connectioned to
    socks_dir.send(token_data)
    response = socks_dir.recv(1024)
    return response

def re_register_function(token, onion, key):
    """
    function to register tokens to new onion address. Must use inital key that
    was sent when registering function
    """
    modified_token_data = {'token':token,'onion': onion, 'req_type':2, 'key':key}
    modified_token_data = json.dumps(modified_token_data)
    socks_dir = socks.socksocket()
    socks_dir.setproxy(socks.PROXY_TYPE_SOCKS5,"127.0.0.1", 9050, True) #9050 is the default Tor proxy can be changed to user preferenance
    socks_dir.connect(("Bento_function_directory_IP", 8080)) # location of Bento function Directory to be connectioned to
    socks_dir.send(bytes(modified_token_data,encoding="utf-8"))
    response = socks_dir.recv(1024)
    return response
