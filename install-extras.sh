#!/bin/sh

SYSTEMD_UNIT_DIR=$(pkg-config --variable=systemdsystemunitdir systemd)
install -D gpuplugd.service $SYSTEMD_UNIT_DIR
install -D gpuplugd.conf /etc/
