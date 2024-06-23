from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pygame import mixer

mixer.init()

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

@app.post("/audio")
def start(filename: str):
    if filename == 'stop':
        mixer.music.stop()
        return Response(f'Stop playing {filename}.')
    mixer.music.load(filename)
    mixer.music.play()
    print(f'Start playing {filename}.')
    return Response(f'Start playing {filename}.')

@app.get("/audio")
def state():
    if mixer.music.get_busy():
        return {'type': 'audio', 'state': 'playing'}
    else:
        return {'type': 'audio', 'state': 'not playing'}