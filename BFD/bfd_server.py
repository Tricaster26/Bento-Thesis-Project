#!/usr/bin/env python3

import socket
import json
import os
import bcrypt

def encrypt(key):
    password = key
    salt = bcrypt.gensalt()
    bytes = password.encode('utf-8')
    hash = bcrypt.hashpw(bytes, salt)
    return hash

def __main():
    HOST = '127.0.0.1'     #local host
    PORT = 8080            # random port

    DIR = "./token_directory"
    keys = "./keys"
    sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))

    try:
        sock.listen()
        print("LISTENING ON PORT 8080...")
        while True:
            conn, addr= sock.accept()
            data = conn.recv(1024).decode('utf-8')
            print(data)
            back_data = bytes("Error",encoding ="utf-8")
            if not data: break
            if not json.loads(data): break #verifies data is sent in json format
            if 'token' in data:
                try:
                    data = json.loads(data)
                    token = data['token']
                    filename = DIR + "/" + token + ".json"
                    req_type = data['req_type']
                    if req_type == 0:
                        json_name = token + ".json"
                        if json_name in os.listdir(DIR):  #checks if token is in list
                            with open(filename,'r') as filein:
                                back_data = json.load(filein)
                            back_data = json.dumps(back_data)
                            conn.send(bytes(back_data, encoding = "utf-8"))
                        else:
                            conn.send(bytes("token unavailable", encoding = "utf-8"))

                    elif req_type == 1:   #registering token req type
                        json_name = token + ".json"
                        if json_name in os.listdir(DIR):
                            conn.send(bytes("token already exists",encoding="utf-8"))
                        else:
                            keyfile = keys + "/" + token + ".json"
                            hash = encrypt(data['key'])
                            hash_json = {'hash': hash.decode()}
                            with open(keyfile, 'w') as outfile:
                                json.dump(hash_json, outfile)

                            json_save =  {'onion': data['onion']} # onion is mandatory

                            if 'function_name' in data:           # optional data such as function name can be dumped in json file
                                func_name  = {'function_name': data['function_name']}
                                json_save.update(func_name)

                            if 'function_code' in data:
                                func_code  = {'function_code': data['function_code']}
                                json_save.update(func_code)

                            with open(filename, 'w') as outfile:
                                json.dump(json_save, outfile)

                            conn.send(bytes("Success",encoding="utf-8"))               # notifies successful registration

                    elif req_type == 2:                        # re-registering request to new domain
                        json_name = token + ".json"
                        if json_name in os.listdir(keys):
                            keyfile = keys + "/" + token + ".json"
                            key = data['key']
                            json_info = None
                            hash = None
                            with open(keyfile) as filein:
                                hash = json.load(filein)
                            hash = hash['hash']         #hash stored in system
                            match = bcrypt.checkpw(key.encode('utf-8'), hash.encode()) #checks if given password matches hash
                            if match:   #password is a match with hash
                                with open(filename,'r') as filein:
                                    json_info = json.load(filein)
                                json_info['onion'] = data['onion']
                                with open(filename,'w') as outfile:
                                    json.dump(json_info, outfile)
                                conn.send(bytes("Success",encoding="utf-8"))
                            else:
                                conn.send("wrong data")
                except:
                    print("exception occured")

    except socket.error:
        print("ERROR")
    finally:
        sock.close()

if __name__ == '__main__':
    __main()
