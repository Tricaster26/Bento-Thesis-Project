import argparse
import logging
import sys
import zlib

sys.path.append("../..")
from bento.client.api import HiddenConnection
from bento.common.protocol import *
import bento.common.util as util

function_name= "browse"
function_code= """
import requests
import zlib
import os

def browse(url, padding):
    body= requests.get(url, timeout=1).content
    compressed= zlib.compress(body)
    final= compressed
    if padding - len(final) > 0:
        final= final + (os.urandom(padding - len(final)))
    else:
        final= final + (os.urandom((len(final) + padding) % padding))
    api.send(final)

"""

@util.timeit
def main():
    logging.basicConfig(format='%(levelname)s:\t%(message)s',
            level=logging.DEBUG)

    parser = argparse.ArgumentParser(
            description='Fetch a website and pad response with dummy bytes')
    parser.add_argument('onion', help="onion address of bento service")
    parser.add_argument('port', type=int, help="hidden server's Tor port")
    parser.add_argument('url', help="website to fetch")
    parser.add_argument('padding', help="pad URL body to ne")
    args = parser.parse_args()

    conn= HiddenConnection(args.onion, args.port)
    call= f"{function_name}('{args.url}', {args.padding})"

    response = conn.send_store_request(function_name, function_code)
    final = conn.send_execute_open_request(response.decode(), call)
    print(zlib.decompress(final))


if __name__ == '__main__':
    main()
