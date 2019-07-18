#!/usr/bin/env python3

import socketserver
import os

CTL_SOCKET_PATH = '/tmp/gpuplug-ctl'
CNT_SOCKET_BASE_PATH = '/tmp/gpuplug-'

container_servers = []

def container_socket_path(i):
    return CNT_SOCKET_BASE_PATH + str(i)

class ContainerSocket(socketserver.BaseRequestHandler):
    def handle(self):
        print('handle container')

class ControlSocket(socketserver.BaseRequestHandler):
    def handle(self):
        self.path = container_socket_path(len(container_servers))
        server = socketserver.UnixStreamServer(self.path, ContainerSocket)
        container_servers.append(server)

        self.request.sendall(str.encode(self.path, 'ascii'))

    def get_path(self):
        return self.path

if __name__ == '__main__':
    ctl_server = socketserver.UnixStreamServer(CTL_SOCKET_PATH, ControlSocket)
    try:
        ctl_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        os.unlink(CTL_SOCKET_PATH)
        for i in range(0, len(container_servers)):
            os.unlink(container_socket_path(i))
        print('bye!')
