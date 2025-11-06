#!/usr/bin/sh

DIR=`dirname $0`

cd $DIR
/home/pi/.local/bin/uvicorn main:app --host 0.0.0.0 --port 8001
