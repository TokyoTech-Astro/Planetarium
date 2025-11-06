from fastapi import FastAPI, Response, BackgroundTasks
import json
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
import subprocess
from gpiozero import PWMLED
from time import sleep

with open('leds.json') as f:
    fjson = json.load(f)

leds = {}
for led in fjson:
    leds[int(led['pin'])] = PWMLED(int(led['pin']))

kousei = None
for led in fjson:
    if led['name'] == '恒星':
        kousei = int(led['pin'])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

STEPS = 100
GAMMA = 4

def handleLED (pin:int, state:bool, fade_time:Union[float,None] = None):
    led = leds[pin]

    if fade_time == None:
        if pin != kousei:
            if state:
                led.on()
            else:
                led.off()
        elif pin == kousei:
            if state:
                led.off()
            else:
                led.on()

    else:
        delay = fade_time / STEPS

        if state == True:
            if pin != kousei:
                for i in range(STEPS+1):
                    time_ratio = i / STEPS
                    brightness = time_ratio ** GAMMA
                    led.value = brightness
                    sleep(delay)
                led.value = 1.0
            elif pin == kousei:
                for i in range(STEPS+1):
                    time_ratio = i / STEPS
                    brightness = 1.0 - time_ratio ** GAMMA
                    led.value = brightness
                    sleep(delay)
                led.value = 0.0
        elif state == False:
            if pin != kousei:
                for i in range(STEPS+1):
                    time_ratio = i / STEPS
                    brightness = (1.0 - time_ratio) ** GAMMA
                    led.value = brightness
                    sleep(delay)
                led.value = 0.0
            elif pin == kousei:
                for i in range(STEPS+1):
                    time_ratio = i / STEPS
                    brightness = 1.0 - (1.0 - time_ratio) ** GAMMA
                    led.value = brightness
                    sleep(delay)
                led.value = 1.0

@app.put("/led/{pin}")
def write(response:Response, background_tasks: BackgroundTasks, pin:int, state:bool, fade_time:Union[float,None] = None):
    global fjson, leds

    for led in fjson:
        if int(led['pin']) != pin:
            continue

        log_message = f"Trun {'on' if state else 'off'} {led['name']}(pin{pin})."

        if fade_time is not None:
            log_message += f" fade time({fade_time})"

        background_tasks.add_task(handleLED, pin, state, fade_time)

        print(log_message)
        return Response(log_message)


@app.get("/led/{pin}")
def state(response:Response, pin:int):
    global leds, fjson
    for led in fjson:
        if int(led['pin']) == pin:
            return {"type": "led", "pin": pin, "name": led['name'], "state": leds[pin].value}

