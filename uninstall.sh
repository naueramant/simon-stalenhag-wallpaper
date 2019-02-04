#! /bin/sh

systemctl stop --user stalenhag.service stalenhag.timer
systemctl disable --user stalenhag.service stalenhag.timer
sudo rm /usr/local/bin/stalenhag
sudo rm /etc/systemd/user/stalenhag.*
