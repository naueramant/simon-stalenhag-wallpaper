#! /bin/sh

sudo cp stalenhag.py /usr/local/bin/stalenhag
sudo cp -p systemd/* /etc/systemd/user
systemctl enable --user stalenhag.service stalenhag.timer
systemctl start --user stalenhag.service stalenhag.timer
