#!/usr/bin/env python3

from gpuplugd import CTL_SOCKET_PATH

import socket

if __name__ == '__main__':
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(CTL_SOCKET_PATH)
    msg = ''
    while True:
        b = sock.recv(1)
        if  b == b'\n':
            print(msg)
            break
        msg += b.decode('ascii')
