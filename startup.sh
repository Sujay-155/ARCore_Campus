#!/bin/bash

# STEP 1: Install system dependencies for Chromedriver ⚙️
echo "INSTALLING SYSTEM DEPENDENCIES"
apt-get update
apt-get install -y libnss3 libgconf-2-4 libfontconfig1

# STEP 2: Install Google Chrome
echo "INSTALLING GOOGLE CHROME"
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install
rm google-chrome-stable_current_amd64.deb
echo "GOOGLE CHROME INSTALLATION COMPLETE"

# STEP 3: Start the Gunicorn server
echo "STARTING GUNICORN"
gunicorn --bind=0.0.0.0 --timeout 600 --workers=1 app:app
