#!/usr/bin/env python3

# Copyright 2019 Aapo Vienamo
# SPDX-License-Identifier: MIT

import configparser
import logging
import os
import socketserver
import threading

CNT_SOCKET_PATH = '/tmp/gpuplug'

def dev_to_nums(path):
    dev = os.lstat(path).st_rdev
    return (os.major(dev), os.minor(dev))

def get_device_cgroup_path(cnt_id):
    path_fmts = [
        '/sys/fs/cgroup/devices/docker/{}/',
        '/sys/fs/cgroup/devices/system.slice/{}/',
    ]
    paths = map(lambda fmt: fmt.format(cnt_id), path_fmts)
    valid_paths = list(filter(os.path.isdir, paths))
    if len(valid_paths) == 0:
        return None
    return valid_paths[0]

class ContainerSocket(socketserver.BaseRequestHandler):
    def handle(self):
        """ TODO GPU allocation tracking """
        dev_nodes = self.server.gpus[0]['devs']

        msg = self.request.makefile().readline().rstrip()
        (verb, cnt_id) = msg.split(':')

        sysfs_files = {'get': '/devices.allow', 'put': '/devices.deny'}
        if not verb in sysfs_files:
            self.request.sendall(str.encode('Fail\n', 'ascii'))
            logging.error('Invalid request \"{}\" from {}'.format(verb, cnt_id))
            return

        path = get_device_cgroup_path(cnt_id)
        if path == None:
            self.request.sendall(str.encode('Fail\n', 'ascii'))
            logging.error('Could not find cgroup device sysfs directory for {}'
                          .format(cnt_id))
            return

        with open(path + sysfs_files[verb], 'w+') as f:
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
