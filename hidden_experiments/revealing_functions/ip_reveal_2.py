#!/usr/bin/env python3

import argparse
import logging
import sys
import zlib

sys.path.append("../..")
from bento.client.api import ClientConnection
from bento.common.protocol import *
import bento.common.util as util

function_name= "ip_reveal_2"
function_code= """
import requests
import zlib


def ip_reveal_2():
    ip_address = socket.gethostbyname(socket.gethostname())

    data = None
    response = requests.get(f"https://checkip.amazonaws.com/")
    data = response.json()


    ip_info = zlib.compress(data)
    api.send(ip_info)
"""

@util.timeit
def main():
    logging.basicConfig(format='%(levelname)s:\t%(message)s',
            level=logging.DEBUG)

    parser = argparse.ArgumentParser(
            description='Fetch a website and pad response with dummy bytes')
    parser.add_argument('onion', help="onion address of bento service")
    parser.add_argument('port', type=int, help="hidden server's Tor port")
    args = parser.parse_args()

    conn= HiddenConnection(args.onion, args.port)
    call= f"{function_name}('{args.url}', {args.padding})"

    response = conn.send_store_request(function_name, function_code)
    final = conn.send_execute_open_request(response.decode(), call)
    print(zlib.decompress(final))

if __name__ == '__main__':
    main()
