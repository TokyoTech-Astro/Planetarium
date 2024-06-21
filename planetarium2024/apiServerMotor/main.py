from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess

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

_proc: subprocess.Popen
_dir:str
_deg:int
_speed:str

@app.post("/motor")
def rotation(dir: str, deg: int, speed: str):
    global _proc, _dir, _deg, _speed
    try:
        _proc.kill()
    except:
        pass
    _proc = subprocess.Popen(["python", "rotate.py", dir, str(deg), speed])
    _dir = dir
    _deg = deg
    _speed = speed
    print(f'Start rotation. (dir:{dir}, deg:{deg}, speed:{speed})')
    return {'type': 'motor', 'state': 'started', "direction": dir, "degree": deg, "speed": speed}