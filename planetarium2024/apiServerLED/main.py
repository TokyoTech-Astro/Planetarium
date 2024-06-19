from fastapi import FastAPI
from gpiozero import DigitalOutputDevice
import json
from fastapi.middleware.cors import CORSMiddleware

with open('leds.json') as f:
    fjson = json.load(f)

leds = {}
for led in fjson:
    leds[int(led['pin'])] = DigitalOutputDevice(int(led['pin']))

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.put("/led/{pin}")
def write(pin:int, state:bool):
    global leds
    if state:
        leds[pin].on()
    else:
        leds[pin].off()
    return

@app.get("/led/{pin}")
def state(pin:int):
    global leds
    for led in fjson:
        if int(led['pin']) == pin:
            return {"pin": pin, "name": led['name'], "state": leds[pin].value}