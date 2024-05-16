# -*- coding: utf-8 -*-
import pygame
import time
import sys
from threading import Thread
import threading

class Audio(Thread):
    def __init__(self,name):
        super(Audio,self).__init__()
        self.name = name

    def run(self):
        pygame.mixer.init()
        file_name = self.name + ".wav"
        print("Playing " + file_name)
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()

if __name__ == "__main__":
    Audio("1おおいぬ座").start()
    time.sleep(10)
