#!usr//bin/bash
sudo iwconfig wlan0 power off
cd /home/pi/Desktop/Planetarium/planetarium2023
python3 client_motor.py
