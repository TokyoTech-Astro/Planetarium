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
        print(f'Turn on. (pin:{pin}, name:{led['name']})')
        return {"type": "led", "pin": pin, "name": led['name'], "state": leds[pin].value}
    else:
        leds[pin].off()
        print(f'Turn off. (pin:{pin}, name:{led['name']})')
        return {"type": "led", "pin": pin, "name": led['name'], "state": leds[pin].value}


@app.get("/led/{pin}")
def state(pin:int):
    global leds
    for led in fjson:
        if int(led['pin']) == pin:
            return {"type": "led", "pin": pin, "name": led['name'], "state": leds[pin].value}