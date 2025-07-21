#!/usr/bin/env python

import json
import requests
import time
import signal
import os
from os.path import join
from dotenv import load_dotenv

dotenv_path = join('./', '.env')
load_dotenv()
SERVER_LED = os.getenv('NEXT_PUBLIC_SERVER_LED')
SERVER_LED_PORT = os.getenv('NEXT_PUBLIC_SERVER_LED_PORT')
SERVER_MOTOR = os.getenv('NEXT_PUBLIC_SERVER_MOTOR')
SERVER_MOTOR_PORT = os.getenv('NEXT_PUBLIC_SERVER_MOTOR_PORT')
SERVER_AUDIO = os.getenv('NEXT_PUBLIC_SERVER_AUDIO')
SERVER_AUDIO_PORT = os.getenv('NEXT_PUBLIC_SERVER_AUDIO_PORT')

with open('src/k2023.json') as f:
    k2023 = json.load(f)

with open('src/leds.json') as f:
    leds = json.load(f)

def sigtermHandler(signal_number, frame):
    for led in leds:
        putLed(led['pin'], False)
    postMotor("stop")
    postAudio("stop")
    print("Auto mode stopped.")
    exit(0)

signal.signal(signal.SIGTERM, sigtermHandler)

black   = '\u001b[30m'
red     = '\u001b[31m'
green   = '\u001b[32m'
yellow  = '\u001b[33m'
blue    = '\u001b[34m'
magenta = '\u001b[35m'
cyan    = '\u001b[36m'
white   = '\u001b[37m'
reset   = '\u001b[0m'

def putLed(pin:int, state:bool):
    print(f'http://{SERVER_LED}:{SERVER_LED_PORT}/led/{pin}?state={state}')
    try:
        if int(pin) != 4:
            res = requests.put(f'http://{SERVER_LED}:{SERVER_LED_PORT}/led/{pin}?state={state}')
            print(f'{yellow}■{reset} Set LED state. (pin:{pin}, state:{state}).')
        else:
            res = requests.put(f'http://pi-controller.local:8002/led/{pin}?state={state}')
            print(f'{yellow}■{reset} Set LED state. (pin:{pin}, state:{state}).')
    except:
        pass

def handleLed(pins:list[int]):
    for pin in pins:
        if pin > 0:
            putLed(pin, True)
        else:
            putLed(-pin, False)

def postMotor(query:str, dir:str="", deg:int=0, speed:str=""):
    try:
        res = requests.post(f'http://{SERVER_MOTOR}:{SERVER_MOTOR_PORT}/motor?query={query}&dir={dir}&deg={deg}&speed={speed}')
        if query == "start":
            print(f'{green}■{reset} Start rotation. (dir:{dir}, deg:{deg}, speed:{speed})')
        elif query == "stop":
            print('Stop rotation.')
    except:
        pass

def handleMotor(deg:int):
    if deg > 0:
        postMotor("start", "forward", deg, "high")
    else:
        postMotor("start", "back", -deg, "high")

def postAudio(filename:str):
    try:
        res = requests.post(f'http://{SERVER_AUDIO}:{SERVER_AUDIO_PORT}/audio?filename={filename}')
        print(f'{blue}■{reset} Playing {filename}.')
    except:
        pass

def handleInterval(interval:str|int):
    if interval == "allLedOff":
        for led in leds:
            putLed(led['pin'], False)
    else:
        print(f'{magenta}■{reset} Interval of {interval} sec.')
        time.sleep(interval)

def autoMode():
    for i in k2023:
        if i.get('star') != None:
            handleLed(i['star'])
        if i.get("motor") != None:
            handleMotor(i["motor"])
        if i.get("audio") != None:
            postAudio(i["audio"]) 
        if i.get("interval") != None:
            handleInterval(i["interval"])
        print("")

autoMode()
