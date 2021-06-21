#!/bin/sh
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install tmux
sudo apt-get install git
pip3 install -r requirements.txt
sudo apt install vsftpd
sudo systemctl start vsftpd
sudo systemctl enable vsftpd
sudo cp /etc/vsftpd.conf  /etc/vsftpd.conf_default
sudo ufw allow 20/tcp
sudo ufw allow 21/tcp
sudo useradd -m griffin
sudo passwd griffin
