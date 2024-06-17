from fastapi import FastAPI
from gpiozero import DigitalOutputDevice
import threading
import time

_pins = [
    DigitalOutputDevice(21),
    DigitalOutputDevice(12),
    DigitalOutputDevice(8),
    DigitalOutputDevice(23)
]
_state: bool = False
_dir: str
_deg: int
_speed: str

app = FastAPI()

@app.post("/motor")
def rotation(dir: str, deg: int, speed: str):
    global _pins, _state, _dir, _deg, _speed
    if _state:
        return {"name": "motor", "error": "(rejected) The motor is already rotating. Wait until it stops.", "direction": _dir, "degree": str(_deg), "speed": _speed}
    _dir = dir
    _deg = deg
    _speed = speed
    threading.Thread(target=rotate).start()
    return

@app.get("/motor")
def state():
    global _state, _dir, _deg, _speed
    if _state:
        return {"name": "motor", "state": "rotate", "direction": _dir, "degree": str(_deg), "speed": _speed}
    else:
        return {"name": "motor", "state": "stop"}
    




def rotate():
    global _pins, _state, _dir, _deg, _speed

    if _deg >= 0:
        step = int(3*_deg/0.2)
    else:
        return
        
    if _speed == "low":
        sleepTime = 0.012
    elif _speed == "medium":
        sleepTime = 0.006
    elif _speed == "high":
        sleepTime = 0.003
    else:
        return

    if _dir == "forward":
        _state = True
        for _ in range(step):
            _pins[0].on()
            _pins[1].on()
            _pins[2].off()
            _pins[3].off()
            time.sleep(sleepTime)

            _pins[0].off()
            _pins[1].on()
            _pins[2].on()
            _pins[3].off()
            time.sleep(sleepTime)

            _pins[0].off()
            _pins[1].off()
            _pins[2].on()
            _pins[3].on()
            time.sleep(sleepTime)

            _pins[0].on()
            _pins[1].off()
            _pins[2].off()
            _pins[3].on()
            time.sleep(sleepTime)
        _state = False
    
    elif _dir == "back":
        _state = True
        for _ in range(step):
            _pins[0].on()
            _pins[1].on()
            _pins[2].off()
            _pins[3].off()
            time.sleep(sleepTime)

            _pins[0].on()
            _pins[1].off()
            _pins[2].off()
            _pins[3].on()
            time.sleep(sleepTime)

            _pins[0].off()
            _pins[1].off()
            _pins[2].on()
            _pins[3].on()
            time.sleep(sleepTime)

            _pins[0].off()
            _pins[1].on()
            _pins[2].on()
            _pins[3].off()
            time.sleep(sleepTime)
        _state = False

    else:
        return