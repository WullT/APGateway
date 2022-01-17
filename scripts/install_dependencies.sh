#!/bin/sh

sudo apt update  # To get the latest package lists
sudo apt install python3-pip -y
pip3 install flask
pip3 install flask_httpauth
pip3 install werkzeug