from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pygame
from threading import Thread

class Audio(Thread):
    def __init__(self,name):
        super(Audio,self).__init__()
        self.name = name

    def run(self):
        pygame.mixer.init()
        file_name = self.name
        print("Playing " + file_name)
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()

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
    Audio(filename).start()
    return

@app.get("/audio")
def state():
    return