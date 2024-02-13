#!/usr/bin/env python3

import argparse
import logging
import sys
import zlib

sys.path.append("../..")
from bento.client.api import ClientConnection
from bento.common.protocol import *
import bento.common.util as util

function_name= "cache"
function_code= """
import hashlib
import socks
import requests
from urllib.parse import urlparse
import urllib
import time
import socket
from cacheout import lru
import socks
import signal
import sys
import os
from cacheout import lru
import signal

curr_url = None
curr_protocol = None

l = lru.LRUCache(maxsize=256, ttl=86400, timer=time.time, default=None) # use this cache to use least recently used cache policy (websites are cached in memory)
# ttl is num seconds in a day

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 8009))
server.listen(10) # we can change the backlog if necessary


def init_cache():
    if(os.path.exists('./cache')):
        list = os.listdir('./cache')
    else:
        os.mkdir('./cache')

init_cache()

def signal_handler(sig, frame):
    print("detected sigint")
    for h in l:
        filename = "./cache/" + h
        f = open(filename, 'wb+')
        f.write(l.get(h))
    l.clear()
    sys.exit(0)

def fetch_file(parsed_url: urllib.parse.ParseResult) -> bytes:
    h = hashlib.sha256()
    filename = None
    global curr_url
    global curr_protocol
    if(curr_url != None):
        filename = curr_url + parsed_url.path
    else:
        filename = parsed_url.netloc + parsed_url.path
    assert(filename != None)
    h.update(filename.encode())
    file_digest = h.hexdigest()
    content = l.get(file_digest)
    if(content == None):
        if(curr_url != None):
            print()
            print("curr_url is: " + curr_url)
            print()
        if(parsed_url.netloc == ''):
            url = curr_protocol + '://' + curr_url + '/' + parsed_url.path
        else:
            url = curr_protocol + '://' + parsed_url.netloc + parsed_url.path
        print(url)
        # set up tor connection
        session = requests.session()
        session.proxies = {}
        session.proxies['http'] = 'socks5h://localhost:9050'
        session.proxies['https'] = 'socks5h://localhost:9050'

        content = session.get(url).content
        session.close()
        print("saving to cache")
        print(file_digest)
        l.set(file_digest, content)
        print()
        print("returning content")
        return content
    return content


def cproxy():
    print("starting cproxy")
    signal.signal(signal.SIGINT, signal_handler)
    while(True):
        client, addr = server.accept()
        print(addr)
        print()
        request = client.recv(1024)
        fields = request.split()
        print(fields)
        print()
        if(len(fields) <= 1):
            client.close()
            continue
        method = fields[0]
        filename = fields[1][1:] # has format -> /www.google.com
        print()
        print("filename is: " + filename.decode('utf-8'))
        print()
        parsed = urlparse(filename.decode('utf-8'))
        print(parsed)
        if(parsed.netloc != ''):
             global curr_url
             global curr_protocol
             curr_url = parsed.netloc
             curr_protocol = parsed.scheme
        content = fetch_file(parsed)
        if(content):
            print("sending 200")
            print()
            client.sendall(b'HTTP/1.0 200 OK\r\n\r\n' + content)
        else:
            print("sending 404")
            print()
            client.sendall(b'HTTP/1.0 404 NOT FOUND\r\n\r\n File Not Found')
        l.evict()
        client.close()
"""

@util.timeit
def main():
    logging.basicConfig(format='%(levelname)s:\t%(message)s',
            level=logging.DEBUG)

    parser = argparse.ArgumentParser(
            description='Fetch a website and pad response with dummy bytes')
    parser.add_argument('host', help="server's IPv4 address")
    parser.add_argument('port', type=int, help="server's port")
    parser.add_argument('url', help="URL to fetch")
    args = parser.parse_args()

    conn= ClientConnection(args.host, args.port)

    token, errmsg= conn.send_store_request(function_name, function_code)
    if errmsg is not None:
        util.fatal(f"Error message from server {errmsg}")

    logging.debug(f"Got token: {token}")

    call= f"{function_name}('{args.url}', {args.padding})"
    session_id, errmsg= conn.send_execute_request(call, token)
    if errmsg is not None:
        util.fatal(f"Error message from server {errmsg}")

    logging.debug(f"Got session_id: {session_id}")

    logging.debug("Getting output...")
    conn.send_open_request(session_id)
    data, session_id, err= conn.get_sessionmsg()
    print(zlib.decompress(data))


if __name__ == '__main__':
    main()
