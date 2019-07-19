#!/usr/bin/env python3

import socket
import sys

SOCKET_PATH = '/tmp/gpuplug'

def get_container_id():
    f = open('/proc/self/cgroup')
    l = f.readline().rstrip()
    f.close()
    return l.split('/')[2]

def gpu_req(verb):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCKET_PATH)
    sock.sendall(str.encode(verb + ':' + get_container_id() + '\n', 'ascii'))
    msg = ''
    while True:
        b = sock.recv(1)
        if len(b) == 0:
            break
        msg += b.decode('ascii')

    sock.close()
    return msg

def main():
    if len(sys.argv) < 2:
        print("Usage: gpuplugc.py get|put")
        return
    ret_msg = gpu_req(sys.argv[1])
    print(ret_msg)
    if ret_msg != 'Ok':
        exit(-1)

if __name__ == '__main__':
    main()
