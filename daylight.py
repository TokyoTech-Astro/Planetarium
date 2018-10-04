import time
import RPi.GPIO as GPIO


class Daylight:
    DAWN_PIN = 24
    DUSK_PIN = 25


    def __init__(self):
        pass

    
    def __enter__(self):
        GPIO.setup(DAWN_PIN, GPIO.OUT)
        GPIO.setup(DUSK_PIN, GPIO.OUT)
        return self


    def __exit__(self, type, value, traceback):
        GPIO.cleanup(DAWN_PIN)
        GPIO.cleanup(DUSK_PIN)


    def dawn():
        GPIO.output(DAWN_PIN, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(DAWN_PIN, GPIO.LOW)
    

    def dust():
        GPIO.output(DUST_PIN, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(DUST_PIN, GPIO.LOW)
