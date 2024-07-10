from fastapi import FastAPI, Response
from gpiozero import DigitalOutputDevice
import json
from fastapi.middleware.cors import CORSMiddleware

with open('leds.json') as f:
    fjson = json.load(f)

leds = {}
for led in fjson:
    leds[int(led['pin'])] = DigitalOutputDevice(int(led['pin']))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.put("/led/{pin}")
def write(response:Response, pin:int, state:bool):
    global leds, fjson
    for led in fjson:
        if int(led['pin']) == pin:
            if state:
                if pin == 4:
                    leds[pin].off()
                else:
                    leds[pin].on()
                print(f"Turn on {led['name']}(pin{pin}).")
                return Response(f"Turn on {led['name']}(pin{pin}).")
            else:
                if pin == 4:
                    leds[pin].on()
                else:
                    leds[pin].off()
                print(f"Turn off {led['name']}(pin{pin}).")
                return Response(f"Turn off {led['name']}(pin{pin}).")


@app.get("/led/{pin}")
def state(response:Response, pin:int):
    global leds, fjson
    for led in fjson:
        if int(led['pin']) == pin:
            return {"type": "led", "pin": pin, "name": led['name'], "state": leds[pin].value}
