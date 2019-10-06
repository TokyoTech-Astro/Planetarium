import time
import RPi.GPIO as GPIO
from gpio_maintaner import GPIOMaintainer


DAWN_PIN = 24
DUSK_PIN = 25


class Daylight:
    def __init__(self):
        pass

    
    def __enter__(self):
        GPIO.setup(DAWN_PIN, GPIO.OUT)
        GPIO.setup(DUSK_PIN, GPIO.OUT)
        return self


    def __exit__(self, type, value, traceback):
        GPIO.cleanup(DAWN_PIN)
        GPIO.cleanup(DUSK_PIN)


    def dawn(self):
        print("daylight on")
        GPIO.output(DAWN_PIN, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(DAWN_PIN, GPIO.LOW)
    

    def dusk(self):
        print("daylight off")
        GPIO.output(DUSK_PIN, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(DUSK_PIN, GPIO.LOW)


if __name__ == "__main__":
    with GPIOMaintainer():
        with Daylight() as dl:
            while True:
                mode = input("on or off or exit")
                if mode == "on":
                    dl.dawn()
                elif mode == "off":
                    dl.dusk()
                else:
                    print("Error")
                