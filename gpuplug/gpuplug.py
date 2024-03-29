#!/usr/bin/env python3

# Copyright 2019 Aapo Vienamo
# SPDX-License-Identifier: MIT

import socket
import sys

try:
    from gpuplug.gpuplugd import SOCKET_PATH
except ImportError:
    from gpuplugd import SOCKET_PATH

def get_container_id():
    with open('/proc/self/cgroup') as f:
        paths = map(lambda l: l.rstrip().split(':'), f.readlines())
        path = list(filter(lambda p: p[2] != '/', paths))[0][2]
    return path

def gpu_req(verb):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCKET_PATH)
    sock.sendall(str.encode(verb + ':' + get_container_id() + '\n', 'ascii'))

    msg = sock.makefile().readline().rstrip()

    sock.close()
    return msg

class GpuCtx:
    def __enter__(self):
        ret_msg = gpu_req('get')
        if ret_msg != 'Ok':
            raise RuntimeError(ret_msg)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        ret_msg = gpu_req('put')
        if ret_msg != 'Ok':
            raise RuntimeError(ret_msg)

def main():
    if len(sys.argv) < 2:
        print("Usage: gpuplugc.py get|put")
        return
    ret_msg = gpu_req(sys.argv[1])
    if ret_msg != 'Ok':
        print(ret_msg)
        exit(-1)

if __name__ == '__main__':
    main()
