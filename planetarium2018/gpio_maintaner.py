import RPi.GPIO as GPIO

class GPIOMaintainer:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)


    def __enter__(self):
        pass


    def __exit__(self, type, value, traceback):
        GPIO.cleanup()