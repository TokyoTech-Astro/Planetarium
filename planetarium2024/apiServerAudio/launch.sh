#!/usr/bin/sh

cd `dirname $0`
/home/pi/.local/bin/uvicorn main:app --host pi-controller.local --port 8001
