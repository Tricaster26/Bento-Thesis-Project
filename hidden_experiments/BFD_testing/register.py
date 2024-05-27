import sys
import os
import json
import socks
import bcrypt
sys.path.append("../..")


def register_function(token, onion):
    """
    Registers function data with hidden service. Cuurently no bento Directory
    exsiting, so tokens just saved locally
    """
    function_data = get_function(token)
    key = "123"
    token_data = {'token':token ,'onion': onion, 'function_name':function_data['name'], 'function_code':function_data['code'], 'req_type':1, 'key':key}
    token_data = json.dumps(token_data)
    socks_dir = socks.socksocket()
    socks_dir.connect(("127.0.0.1", 8080)) # location of Bento function Directory to be connectioned to
    socks_dir.send(bytes(token_data,encoding="utf-8"))
    response = socks_dir.recv(1024)
    print(response)
    return response

def re_register_function(token, onion, key):
    """
    function to register tokens to new onion address. Must use inital key that
    was sent when registering function
    """
    modified_token_data = {'token':token,'onion': onion, 'req_type':2, 'key':key}
    modified_token_data = json.dumps(modified_token_data)
    socks_dir = socks.socksocket()
    socks_dir.connect(("127.0.0.1", 8080)) # location of Bento function Directory to be connectioned to
    socks_dir.send(bytes(modified_token_data,encoding="utf-8"))
    response = socks_dir.recv(1024)
    print(response)
    return response


def get_function(token):
    """
    retrieve function from storage medium corresponding to the token
    """
    filename= f'./example_tokens/{token}.json'
    if os.path.exists(filename):
        with open(filename) as filein:
            function= json.load(filein)
        return function
    else:
        return None

def receive_onion(token):
    modified_token_data = {'token':token, 'req_type':0,}
    modified_token_data = json.dumps(modified_token_data)
    socks_dir = socks.socksocket()
    socks_dir.connect(("127.0.0.1", 8080)) # location of Bento function Directory to be connectioned to
    socks_dir.send(bytes(modified_token_data,encoding="utf-8"))
    response = socks_dir.recv(1024)
    print(response)
    return response

register_function('0ae41279-f0fa-4d94-b337-8db0fa27a856', "lbytd7kaelqx3ylaj44xclfrfcgv4hjv57svnjfbg2msbwb2rktivvad.onion")
re_register_function('0ae41279-f0fa-4d94-b337-8db0fa27a856', "ifbry5furwsvjgfvhodjbg7wfz5ycbkq7hcpqdvksycmksytq6sshxqd.onion", "123" )
receive_onion('0ae41279-f0fa-4d94-b337-8db0fa27a856')
