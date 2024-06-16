from fastapi import FastAPI
from gpiozero import DigitalOutputDevice
import json

with open('../leds.json') as f:
    leds = json.load(f)

for pin in leds.items():
    leds[pin] = DigitalOutputDevice(pin)

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
    return {"pin": pin, "state": leds[pin].value}