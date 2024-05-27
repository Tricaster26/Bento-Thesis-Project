"""
Api to interface with a bento server
"""

import socket
import socks
import stem
import requests

from bento.common.protocol import *

class HiddenConnection:
    """
    represents a connection with a Bento Hidden Service in order to allow exchanging requests/responses
    with a Bento server as well as data with an executing function
    """
    def __init__(self, onion: str, port: int):
        self.url = onion
        self.proxies = {
            'http': 'socks5h://127.0.0.1:' + str(port),  # Replace with your proxy address and port
            'https': 'socks5h://127.0.0.1:' + str(port)
        }

    def send_exec_request(self, token , call):
        """
        sends only an execution request given a function call and token, waiting for a response
        """
        url = self.url + "/exec"
        post_data = {0: token , 1: call}
        try:
            response = requests.post(url, json= post_data, proxies=self.proxies) # Format of request altered on HS side
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as errex:
            print("Onion service not valid")

    def send_execute_open_request(self, token , call):
        """
        sends an execution request followed by an open request waiting for response data if exists.
        """
        url = self.url + "/open"
        post_data = {0: token , 1: call}
        print(post_data)
        try:
            response = requests.post(url, json= post_data, proxies=self.proxies) # Format of request altered on HS side
            response.raise_for_status()
            return ( response.content)
        except requests.exceptions.RequestException as errex:
            print("Onion service not valid")

    def send_store_request(self, name , code):
        """
        sends an store request and returns response with token in content.
        """
        url = self.url + "/store"
        post_data = {0: name , 1: code}
        try:
            response = requests.post(url, json= post_data, proxies=self.proxies) # Format of request altered on HS side
            response.raise_for_status()
            return (response.content)
        except requests.exceptions.RequestException as errex:
            print("Onion service not valid")

    def send_register_request(self, token):
        """
        sends a register request followed by an open request waiting for response data.
        """
        url = self.url + "/register"
        post_data = {0: token}
        try:
            response = requests.post(url, json= post_data, proxies=self.proxies) # Format of request altered on HS side
            response.raise_for_status()
        except requests.exceptions.RequestException as errex:
            print("Onion service not valid")
        return (response.content)

    def send_custom_request(self, path, token, call):
        """
        For custom paths the server create/allows a client to use
        """
        url = self.url + "/" + path
        post_data = {0: arguments, 1:token, 2:call}
        try:
            response = requests.post(url, json= post_data, proxies=self.proxies) # Format of request altered on HS side
            response.raise_for_status()
        except requests.exceptions.RequestException as errex:
            print("Onion service not valid")
        return (response.content)


class BFDConnection:
    """
    represents a connection with the BFD server. Used by client to receive details of a token
    """
    def __init__(self, address: str, port: int):
        self.conn= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((address, port))

    def request_token(self,token):
        self.conn.send({'token': token, 'req_type': 0})
        json_data = self.recv(1024)
        return json_data

class ClientConnection:
    """
    represents a connection with a Bento server in order to allow exchanging requests/responses
    with a Bento server as well as data with an executing function
    """

    def __init__(self, address: str, port: int):
        self.conn= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((address, port))


    def send_store_request(self, name, code):
        """
        send a synchronous store request which expects a store response or error from the server
        """
        request= StoreRequest(name, code)
        self._send_request(request)
        response= self._get_response()
        if response.resp_type != Types.Store:
            raise Exception("Request-Response types don't match")
        return (response.token, None) if response.success == True else (None, response.errmsg)


    def send_execute_request(self, call, token):
        """
        send a synchronous execute request which expects a execute response or error from the server
        """
        request= ExecuteRequest(call, token)
        self._send_request(request)
        response= self._get_response()
        if response.resp_type != Types.Execute:
            raise Exception("Request-Response types don't match")
        return (response.function_id, None) if response.success == True else (None, response.errmsg)

    def send_open_request(self, function_id):
        """
        send an asynchronous open request that informs the server that the client wants to begin
        exchanging data with a funciton
            - no response expected, any errors will be sent in subsequent function error messages
        """
        request= OpenRequest(function_id)
        self._send_request(request)


    def send_close_request(self, function_id):
        """
        send an asynchronous close request that informs the server that the client would like to
        stop exchanging data with a function
            - no response expected, messages may still be sent in the overlap between a server
              receiving a close request and sending messages
        """
        request= CloseRequest(function_id)
        self._send_request(request)

    def send_register_request(self, token, onion):
        request = RegisterRequest(token)
        self._send_request(request)


    def send_input(self, function_id, data):
        """
        send data to an executing function assuming communication with the function is open
        """
        if len(data) == 0:
            return 0

        if isinstance(data, str):
            data= data.encode()
        msg= Input(function_id, data)
        return self.conn.sendall(msg.serialize())


    def recv_output(self):
        """
        get output data from an executing function assuming there is a function instance running
            - return output data and whether data is stderr or stdout, raise exception if server error
        """
        hdr= self._recv_all(FunctionMessage.HeaderLen)
        if hdr is None:
            raise Exception('failed to recv header')

        msg_type, length, err= FunctionMessage.unpack_hdr(hdr)
        if err is not None:
            raise Exception(f'unpacking header failed: {err}')

        data= self._recv_all(length)
        print(data)
        if data is None:
            raise Exception('failed to recv response data')

        if msg_type == MsgTypes.Output:
            msg= Output.deserialize(data)
            return msg.data, False
        elif msg_type == MsgTypes.Error:
            msg= Error.deserialize(data)
            return msg.data, True
        elif msg_type == MsgTypes.FunctionErr:
            msg= FunctionErr.deserialize(data)
            raise Exception(f"err from server: {msg.data}")
        else:
            raise Exception(f"bad message type from server")


    def _send_request(self, request):
        """
        send wrapper
        """
        self.conn.sendall(request.serialize())


    def _get_response(self):
        """
        attempt to receive response data
        """
        hdr= self._recv_all(Response.HeaderLen)
        if hdr is None:
            raise Exception("failed to recv header")

        resp_type, errbyte, length, err= Response.unpack_hdr(hdr)
        if err is not None:
            raise Exception(f"unpacking header failed: {err}")

        data= self._recv_all(length)
        if data is None:
            raise Exception("failed to recv response data")

        if errbyte == 0x0:
            if resp_type == Types.Execute:
                return ExecuteResponse.deserialize(data)
            elif resp_type == Types.Store:
                return StoreResponse.deserialize(data)
            return ExecuteResponse.deserialize(data)
        else:
            return ErrorResponse.deserialize(data, resp_type)


    def _recv_all(self, n):
        """
        recv wrapper
        """
        data = bytearray()
        while len(data) < n:
            packet= self.conn.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
