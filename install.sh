#!/bin/bash
mkdir -p instance/media
[ -f instance/blacklist.txt ] || touch instance/blacklist.txt
cp -i config.py instance/config.py
cp -i deployment/kcarchive.conf /etc/nginx/conf.d/kcarchive.conf
cp -i deployment/kcarchive.service /etc/systemd/system/kcarchive.service
exit 0
