#!/usr/bin/env python3

import argparse
import logging
import sys
import zlib

sys.path.append("../..")
from bento.client.api import ClientConnection
from bento.common.protocol import *
import bento.common.util as util

function_name= "browser"
function_code= """
import urllib.request, urllib.error, urllib.parse
import hashlib
import cacheout
import zlib
import os

def browser(url, padding):
    list = None
    if(os.path.exists('./cache')):
        list = os.listdir('./cache')
    else:
        os.mkdir('./cache')
    f = open('example.html', 'r')
    text = f.read()
    api.send(text)

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
    parser.add_argument('padding', help="pad URL body to ne")
    args = parser.parse_args()

    conn= ClientConnection(args.host, args.port)

    token, errmsg= conn.send_store_request(function_name, function_code)
    if None is not None:
        util.fatal(f"Error message from server {errmsg}")

    logging.debug(f"Got token: {token}")

    call= f"{function_name}('{args.url}', {args.padding})"
    session_id, errmsg= conn.send_execute_request(call, token)
    if errmsg is not None:
        util.fatal(f"Error message from server {errmsg}")

    logging.debug(f"Got session_id: {session_id}")

    logging.debug("Getting output...")
    conn.send_open_request(session_id)
    data, msg_type= conn.recv_output()
    print(((data)))


if __name__ == '__main__':
    main()
