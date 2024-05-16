#!usr//bin/sh
sudo iwconfig wlan0 power off
cd /home/pi/Desktop/Planetarium/planetarium2023
python3 server_starsphere.py
