#!/usr/bin/env python3

import socketserver
import os

CTL_SOCKET_PATH = '/tmp/gpuplug-ctl'

class ControlSocket(socketserver.BaseRequestHandler):
    msg = ''
    def handle(self):
        print('handle')
        print(self.request)
        while True:
            b = self.request.recv(1)
            if len(b) == 0:
                print(self.msg)
                break
            self.msg += b.decode('ascii')

if __name__ == '__main__':
    ctl_server = socketserver.UnixStreamServer(CTL_SOCKET_PATH, ControlSocket)
    try:
        ctl_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        ctl_server.shutdown()
        os.unlink(CTL_SOCKET_PATH)
        print('bye!')
