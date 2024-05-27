#!/usr/bin/env python3

import argparse
import logging
import sys
import zlib
import time
import statistics

sys.path.append("../..")
from bento.client.api import HiddenConnection, ClientConnection
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

#Must remove hidden service from directory to get time for first connection
def main():
    start_time = time.time()
    logging.basicConfig(format='%(levelname)s:\t%(message)s',
            level=logging.DEBUG)

    conn= HiddenConnection("http://lbytd7kaelqx3ylaj44xclfrfcgv4hjv57svnjfbg2msbwb2rktivvad.onion", "9050")
    call= f"{function_name}('https://example.com?=ultrasurf', 1)"

    response = conn.send_exec_request(call, "0ae41279-f0fa-4d94-b337-8db0fa27a856")

    end_time = time.time()
    print("Time_1 : " + str((end_time -  start_time) *1000) + "ms")
    return ((end_time -  start_time) * 1000)


def regular():
    start_time = time.time()
    logging.basicConfig(format='%(levelname)s:\t%(message)s',
            level=logging.DEBUG)
    conn= ClientConnection("16.171.136.217", 8888)
    call= f"{function_name}('https://example.com?=ultrasurf', 1)"
    session_id, errmsg= conn.send_execute_request(call, "0ae41279-f0fa-4d94-b337-8db0fa27a856")
    if None is not None:
        util.fatal(f"Error message from server {errmsg}")
    logging.debug(f"Got token: {token}")

    end_time = time.time()
    print("Time_2 : " + str((end_time -  start_time) *1000) + "ms")
    return ((end_time -  start_time) * 1000)


if __name__ == '__main__':
    list = []
    for i in range(10):
        test = main()
        list.append(test)
    print(statistics.mean(list))
