from fastapi import FastAPI
from gpiozero import DigitalOutputDevice
import json

with open('../leds.json') as f:
    fjson = json.load(f)

leds = {}
for led in fjson:
    leds[int(led['pin'])] = DigitalOutputDevice(int(led['pin']))

app = FastAPI()

@app.put("/led/{pin}")
def write(pin:int, state:bool):
    if state:
        leds[pin].on()
    else:
        leds[pin].off()
    return

@app.get("/led/{pin}")
def state(pin:int):
    for led in fjson:
        if int(led['pin']) == pin:
            return {"name": led['name'], "state": leds[pin].value}