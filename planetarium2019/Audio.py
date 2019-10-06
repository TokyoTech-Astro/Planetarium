import pygame
import time
import sys
from threading import Thread
import threading

class Audio(Thread):
    def __init__(self,name):
        super().__init__()
        self.name = name

    def run(self):
        pygame.mixer.init()
        file_name = self.name + ".mp3"
        print("Playing " + file_name)
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()
