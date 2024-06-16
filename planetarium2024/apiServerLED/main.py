from fastapi import FastAPI
from gpiozero import DigitalOutputDevice

app = FastAPI()

pins = {}

@app.put("/led/{pin}")
def write(pin:int, state:bool):
    if not(pin in pins):
        pins[pin] = DigitalOutputDevice(pin)

    if state:
        pins[pin].on()
    else:
        pins[pin].off()

    return

@app.get("/led/{pin}")
def state(pin:int):
    if not(pin in pins):
        pins[pin] = DigitalOutputDevice(pin)

    return {"pin": pin, "state": pins[pin].value}