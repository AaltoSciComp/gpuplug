#!/usr/bin/env python3

import logging
import os
import socketserver
import threading

CNT_SOCKET_PATH = '/tmp/gpuplug'

class ContainerSocket(socketserver.BaseRequestHandler):
    def handle(self):
        PATH = '/sys/fs/cgroup/devices/docker/'

        msg = self.request.makefile().readline().rstrip()
        (verb, cnt_id) = msg.split(':')

        sysfs_files = {'get': '/devices.allow', 'put': '/devices.deny'}
        if not verb in sysfs_files:
            self.request.sendall(str.encode('Fail\n', 'ascii'))

        with open(PATH + cnt_id + sysfs_files[verb], 'w+') as f:
            try:
                """ XXX Don't hardcode device numbers """
                f.write('a 195:* rwm')
                f.write('a 236:* rwm')
                self.request.sendall(str.encode('Ok\n', 'ascii'))
                logging.info('{} gpu for container id: {}'.format(
                        verb.capitalize(), cnt_id))
            except Exception:
                self.request.sendall(str.encode('Fail\n', 'ascii'))
                logging.exception('Failed to {} gpu for container id: {}'.format(
                        verb, cnt_id))

class ThreadedUnixServer(socketserver.ThreadingMixIn,
                         socketserver.UnixStreamServer):
    pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    cnt_server = ThreadedUnixServer(CNT_SOCKET_PATH, ContainerSocket)
    try:
        logging.info('Running')
        cnt_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        os.unlink(CNT_SOCKET_PATH)
        logging.info('Bye!')
