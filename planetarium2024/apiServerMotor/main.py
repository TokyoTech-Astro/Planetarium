from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from motorDriver import Motor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

motor = Motor()

@app.post("/motor")
def rotation(response:Response, query:str, dir:str = None, deg:int = None, time:float = None):
    if query == "start":
        motor.rotate(dir,deg,time)
        print(f'Start rotation. (direction={motor.dir}, degree={motor.deg}, time={motor.time})')
        return Response(f'Start rotation. (direction={motor.dir}, degree={motor.deg}, time={motor.time})')
    
    elif query == "stop":
        if motor.proc.returncode == None:
            motor.stop()
            print('Stop rotation.')
            return Response('Stop rotation.')
        else:
            return Response('Not rotating.')

    else:
        pass