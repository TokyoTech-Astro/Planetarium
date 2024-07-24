#!/usr/bin/sh

cd `dirname $0`
/home/pi/.local/bin/uvicorn main:app --host pi-starsphere.local --port 8000
