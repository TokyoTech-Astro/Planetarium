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

    

if __name__ == "__main__":
    Audio("famiyu").start()
    time.sleep(5)
    t = 0
    while t <= 10: 
        print("1")
        t += 1