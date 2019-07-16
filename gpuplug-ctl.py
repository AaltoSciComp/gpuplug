#!/usr/bin/env python3

from gpuplugd import CTL_SOCKET_PATH

import socket

if __name__ == '__main__':
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(CTL_SOCKET_PATH)
    sock.sendall(str.encode('get', 'ascii'))
