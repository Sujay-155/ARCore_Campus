#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "--- STARTING COMPREHENSIVE STARTUP SCRIPT ---"

# 1. Update package lists
echo "--- 1. UPDATING APT PACKAGES ---"
apt-get update

# 2. Install a complete set of dependencies for Headless Chrome
echo "--- 2. INSTALLING ALL DEPENDENCIES ---"
apt-get install -y \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libgconf-2-4 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    wget \
    xdg-utils
echo "--- DEPENDENCIES INSTALLATION COMPLETE ---"

# 3. Install Google Chrome
echo "--- 3. INSTALLING GOOGLE CHROME ---"
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install
rm google-chrome-stable_current_amd64.deb
echo "--- GOOGLE CHROME INSTALLATION COMPLETE ---"

# 4. Start the Gunicorn server
echo "--- 4. STARTING GUNICORN SERVER ---"
gunicorn --bind=0.0.0.0 --timeout 600 --workers=1 app:app

echo "--- STARTUP SCRIPT FINISHED ---"
