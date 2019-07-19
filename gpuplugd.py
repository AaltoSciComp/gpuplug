#!/usr/bin/env python3

import socketserver
import os
import threading

CTL_SOCKET_PATH = '/tmp/gpuplug-ctl'
CNT_SOCKET_BASE_PATH = '/tmp/gpuplug-'

container_servers = []

def container_socket_path(i):
    return CNT_SOCKET_BASE_PATH + str(i)

class ContainerSocket(socketserver.BaseRequestHandler):
    def handle(self):
        PATH = '/sys/fs/cgroup/devices/docker/'
        msg = ''
        while True:
            b = self.request.recv(1)
            if len(b) == 0:
                break
            msg += b.decode('ascii')
        (verb, cnt_id) = msg.split(':')
        if verb == 'get':
            with open(PATH + cnt_id + '/devices.allow', 'w+') as f:
                """ XXX Don't hardcode device numbers """
                f.write('a 195:* rwm')
                f.write('a 236:* rwm')
            print('Bind gpu for container id: {}'.format(cnt_id))

class ThreadedUnixServer(socketserver.ThreadingMixIn,
                         socketserver.UnixStreamServer):
    pass

class ControlSocket(socketserver.BaseRequestHandler):
    def handle(self):
        self.path = container_socket_path(len(container_servers))
        server = ThreadedUnixServer(self.path, ContainerSocket)
        self.thread = threading.Thread(target = server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        container_servers.append(self)

        self.request.sendall(str.encode(self.path, 'ascii'))
        print('Create container socket: {}'.format(self.path))

    def get_path(self):
        return self.path

if __name__ == '__main__':
    ctl_server = ThreadedUnixServer(CTL_SOCKET_PATH, ControlSocket)
    try:
        ctl_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        os.unlink(CTL_SOCKET_PATH)
        for i in range(0, len(container_servers)):
            container_servers[i].server.shutdown()
            os.unlink(container_socket_path(i))
        print('bye!')
