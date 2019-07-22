#!/usr/bin/env python3

import socketserver
import os
import threading
import grp

CTL_SOCKET_PATH = '/tmp/gpuplug-ctl'
CNT_SOCKET_BASE_PATH = '/tmp/gpuplug-'

container_servers_lock = threading.Lock()
container_servers = []

def container_socket_path(i):
    return CNT_SOCKET_BASE_PATH + str(i)

class ContainerSocket(socketserver.BaseRequestHandler):
    def handle(self):
        PATH = '/sys/fs/cgroup/devices/docker/'
        msg = ''
        while True:
            b = self.request.recv(1)
            if len(b) == 0 or b == b'\n':
                break
            msg += b.decode('ascii')
        (verb, cnt_id) = msg.split(':')
        if verb == 'get':
            with open(PATH + cnt_id + '/devices.allow', 'w+') as f:
                try:
                    """ XXX Don't hardcode device numbers """
                    f.write('a 195:* rwm')
                    f.write('a 236:* rwm')
                    self.request.sendall(str.encode('Ok', 'ascii'))
                    print('Bind gpu for container id: {}'.format(cnt_id))
                except:
                    self.request.sendall(str.encode('Fail', 'ascii'))
                    print('Failed to bind gpu for container id: {}'.format(cnt_id))
        elif verb == 'put':
            with open(PATH + cnt_id + '/devices.deny', 'w+') as f:
                try:
                    """ XXX Don't hardcode device numbers """
                    f.write('a 195:* rwm')
                    f.write('a 236:* rwm')
                    self.request.sendall(str.encode('Ok', 'ascii'))
                    print('Unbind gpu for container id: {}'.format(cnt_id))
                except:
                    self.request.sendall(str.encode('Fail', 'ascii'))
                    print('Failed to unbind gpu for container id: {}'.format(cnt_id))
        else:
            self.request.sendall(str.encode('Fail', 'ascii'))

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
        with container_servers_lock:
            container_servers.append(self)

        self.request.sendall(str.encode(self.path + '\n', 'ascii'))
        print('Create container socket: {}'.format(self.path))

    def get_path(self):
        return self.path

if __name__ == '__main__':
    ctl_server = ThreadedUnixServer(CTL_SOCKET_PATH, ControlSocket)
    try:
        uid = os.stat(CTL_SOCKET_PATH).st_uid
        gid = grp.getgrnam('docker').gr_gid
        os.chown(CTL_SOCKET_PATH, uid, gid)
        os.chmod(CTL_SOCKET_PATH, 0o675)
        ctl_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        os.unlink(CTL_SOCKET_PATH)
        with container_servers_lock:
            for s in container_servers:
                s.server.shutdown()
                os.unlink(s.path)
        print('bye!')
