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
    if query == "start":
        global _proc, _dir, _deg, _speed
        try:
            _proc.terminate()
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
            if _proc.poll() == None:
                _proc.terminate()
                print('Stop rotation.')
                return Response('Stop rotation.')
            else:
                return Response('Not rotating.')
        except:
            return Response('Not rotating.')

    else:
        pass