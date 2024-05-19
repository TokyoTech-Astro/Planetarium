#!usr//bin/bash
sudo iwconfig wlan0 power off
cd ./planetarium2023
python3 client_motor.py
