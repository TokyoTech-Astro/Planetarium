#!usr//bin/sh

#2023年のプラネタリウムの自動起動スクリプト

sudo iwconfig wlan0 power off
cd ./planetarium2023
python3 server_starsphere.py
