#!/bin/sh

sudo apt update  # To get the latest package lists
sudo apt install git python3-pip -y
pip3 install flask
pip3 install flask_httpauth
pip3 install werkzeug

cd /home/pi
git clone https://github.com/WullT/APGateway.git

sudo cp /home/pi/APGateway/services/discovery.service /etc/systemd/system/
sudo cp /home/pi/APGateway/services/capture.service /etc/systemd/system/
sudo cp /home/pi/APGateway/services/configserver.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable discovery.service
sudo systemctl enable capture.service
sudo systemctl enable configserver.service

sudo systemctl start discovery.service
sudo systemctl start configserver.service
sudo systemctl start capture.service
