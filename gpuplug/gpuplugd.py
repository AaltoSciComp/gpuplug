#!/usr/bin/env python3

# Copyright 2019 Aapo Vienamo
# SPDX-License-Identifier: MIT

import argparse
import configparser
import logging
import os
import socketserver
import threading

SOCKET_PATH = '/run/gpuplug.sock'

def dev_to_nums(path):
    dev = os.lstat(path).st_rdev
    return (os.major(dev), os.minor(dev))

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

        path = '/sys/fs/cgroup/devices/{}/{}'.format(cnt_id, sysfs_files[verb])

        with open(path, 'w+') as f:
            try:
                for dev_nums in map(dev_to_nums, dev_nodes):
                    cgroup_device_cfg = 'c {0[0]}:{0[1]} rmw'.format(dev_nums)
                    f.write(cgroup_device_cfg)
                    logging.debug(cgroup_device_cfg)
                self.request.sendall(str.encode('Ok\n', 'ascii'))
                logging.info('{} gpu for container id: {}'.format(
                        verb.capitalize(), cnt_id))
            except Exception:
                self.request.sendall(str.encode('Fail\n', 'ascii'))
                logging.exception('Failed to {} gpu for container id: {}'.format(
                        verb, cnt_id))

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

    for idx, gpu in gpus.items():
        for dev in gpu['devs']:
            assert(os.path.exists(dev),
                   "Could not find {} device".format(dev))

    return gpus

def main():
    desc = 'gpuplug host server for dynamic container GPU binding'
    parser = argparse.ArgumentParser(description = desc)
    parser.add_argument('-c', '--conf', metavar = 'CONF',
                        default = '/etc/gpuplugd.conf',
                        help = 'config file location')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    gpus = parse_gpu_devs(args.conf)
    cnt_server = socketserver.UnixStreamServer(SOCKET_PATH, ContainerSocket)
    cnt_server.gpus = gpus
    cnt_server_thread = threading.Thread(name = 'cnt_server',
                                         target = cnt_server.serve_forever)

    try:
        logging.info('Running')
        cnt_server_thread.start()
        '''
        This join won't ever actually complete. The join is here just to keep
        the main thread blocked inside the try-block so the KeyboardInterrupt
        is caught and the server thread is shut down from the exception handler.
        '''
        cnt_server_thread.join()
    except KeyboardInterrupt:
        cnt_server.shutdown()
        cnt_server_thread.join()
        pass
    finally:
        os.unlink(SOCKET_PATH)
        logging.info('Bye!')

if __name__ == '__main__':
    main()
