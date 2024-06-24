from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

_proc: subprocess.Popen
_dir:str
_deg:int
_speed:str

@app.post("/motor")
def rotation(response:Response, query:str, dir:str="", deg:int=0, speed:str=""):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'

    if query == "start":
        global _proc, _dir, _deg, _speed
        try:
            _proc.kill()
        except:
            pass
        _proc = subprocess.Popen(["python", "rotate.py", dir, str(deg), speed])
        _dir = dir
        _deg = deg
        _speed = speed
        print(f'Start rotation. (direction={dir}, degree={deg}, speed={speed})')
        return Response(f'Start rotation. (direction={dir}, degree={deg}, speed={speed})')
    
    elif query == "stop":
        try:
            _proc.kill()
            print('Stop rotation')
            return Response('Stop rotation')
        except:
            return Response('Not rotating.')

    else:
        pass

@app.options("/motor")
def opt(response:Response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return Response()