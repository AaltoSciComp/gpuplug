#!/usr/bin/env python3

import configparser
import logging
import os
import socketserver
import threading

CNT_SOCKET_PATH = '/tmp/gpuplug'

def dev_to_nums(path):
    dev = os.lstat(path).st_rdev
    return (os.major(dev), os.minor(dev))

class ContainerSocket(socketserver.BaseRequestHandler):
    def handle(self):
        PATH = '/sys/fs/cgroup/devices/docker/'
        """ TODO GPU allocation tracking """
        dev_nodes = self.server.gpus[0]['devs']

        msg = self.request.makefile().readline().rstrip()
        (verb, cnt_id) = msg.split(':')

        sysfs_files = {'get': '/devices.allow', 'put': '/devices.deny'}
        if not verb in sysfs_files:
            self.request.sendall(str.encode('Fail\n', 'ascii'))

        with open(PATH + cnt_id + sysfs_files[verb], 'w+') as f:
            try:
                for dev_nums in map(dev_to_nums, dev_nodes):
                    f.write('a {0[0]}:{0[1]} rmw'.format(dev_nums))
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

def parse_gpu_devs(path):
    cfg = configparser.ConfigParser(allow_no_value = True)
    cfg.read(path)

    gpu_sections = filter(lambda section: 'gpu-' in section, cfg.sections())
    gpus = {}
    for section in gpu_sections:
        try:
            idx = int(section.split('-')[1])
            gpus[idx] = {}
            gpus[idx]['devs'] = [node for (node, _) in cfg.items(section)]
        except Exception:
            logging.exception('Failed to parse config file: {}'.format(path))

    return gpus

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    gpus = parse_gpu_devs('gpuplugd.conf') # TODO path
    cnt_server = ThreadedUnixServer(CNT_SOCKET_PATH, ContainerSocket)
    cnt_server.gpus = gpus

    try:
        logging.info('Running')
        cnt_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        os.unlink(CNT_SOCKET_PATH)
        logging.info('Bye!')
