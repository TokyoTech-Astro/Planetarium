#!usr//bin/sh
sudo iwconfig wlan0 power off
cd ./planetarium2023
python3 server_starsphere.py
