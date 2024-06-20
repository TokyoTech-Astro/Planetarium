from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gpiozero import DigitalOutputDevice
import threading
import time
        
_pins = [
    DigitalOutputDevice(21),
    DigitalOutputDevice(12),
    DigitalOutputDevice(8),
    DigitalOutputDevice(23)
]
_dir = "forward"
_deg = 0
_steps = 0
_speed = "medium"
_thread: threading.Thread

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

@app.post("/motor")
def rotation(dir: str, deg: int, speed: str):
    global _dir, _deg, _steps, _speed, _thread
    try:
        _thread
    except:
        _thread = threading.Thread(target=rotate)
        _thread.start()
    _dir = dir
    _deg = deg
    _steps = 5*deg
    _speed = speed
    print(f'Start otationg (dir:{_dir}, deg:{_deg}, speed:{_speed})')
    return {'type': 'motor', 'state': 'started', "direction": _dir, "degree": _deg, "speed": _speed}

@app.get("/motor")
def state():
    global _dir, _deg, _steps, _speed
    if _steps > 0:
        return {"type": "motor", "state": "rotating", "direction": _dir, "degree": _deg, "speed": _speed}
    else:
        return {"type": "motor", "state": "stop"}
    



def rotate():
    global _pins,_dir,_steps,_speed
    while True:
        if _steps > 0:
            _steps-=1

            if _speed == "low":
                sleepTime = 0.012
            elif _speed == "medium":
                sleepTime = 0.006
            elif _speed == "high":
                sleepTime = 0.003
            else:
                return
            
            if _dir == "forward":
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
            
            elif dir == "back":
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

            else:
                return
        
        else:
            time.sleep(0.02)