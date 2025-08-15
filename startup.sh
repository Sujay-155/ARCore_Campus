#!/bin/bash

# STEP 1: Install Google Chrome
echo "INSTALLING GOOGLE CHROME"
apt-get update
apt-get install -y wget unzip
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install
rm google-chrome-stable_current_amd64.deb
echo "GOOGLE CHROME INSTALLATION COMPLETE"

# STEP 2: Start the Gunicorn server
echo "STARTING GUNICORN"
gunicorn --bind=0.0.0.0 --timeout 120 --workers=1 app:app