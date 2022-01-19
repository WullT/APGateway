#!/bin/sh

#sudo cp /home/pi/APGateway/services/discovery.service /etc/systemd/system/
sudo cp /home/pi/APGateway/services/capture.service /etc/systemd/system/
sudo cp /home/pi/APGateway/services/configserver.service /etc/systemd/system/
sudo cp /home/pi/APGateway/services/registrationserver.service /etc/systemd/system/

sudo systemctl daemon-reload
#sudo systemctl enable discovery.service
sudo systemctl enable registrationserver.service
sudo systemctl enable capture.service
sudo systemctl enable configserver.service

#sudo systemctl start discovery.service
sudo systemctl start registrationserver.service
sudo systemctl start configserver.service
sudo systemctl start capture.service
