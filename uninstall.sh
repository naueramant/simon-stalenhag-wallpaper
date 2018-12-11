#! /bin/sh

systemctl stop --user stalenhag.timer
systemctl disable --user stalenhag.timer
sudo rm /usr/local/bin/stalenhag
sudo rm /etc/systemd/user/stalenhag.*
