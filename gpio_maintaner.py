import queue
from threading import Thread
import RPi.GPIO as GPIO


class GPIOMaintainer:
    def __init__(self):
        self.queue = queue.Queue()
        self.con = True
        pass


    def __enter__(self):
        GPIO.setmode(GPIO.BCM)
        self.service = Thread(target=self.controllerService, args=())
        self.service.start()


    def __exit__(self, type, value, traceback):
        self.con = False
        GPIO.cleanup()

    
    def controllerService(self):
        while self.con:
            p1, p2, p3 = self.queue.get()
            if p1 == "setup":
                GPIO.setup(p2, p3)
            elif p1 == "output":
                GPIO.output(p2, p3)
            elif p1 == "cleanup":
                if p2 == None:
                    GPIO.cleanup()
                else:
                    GPIO.cleanup(p2)