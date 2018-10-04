import RPi.GPIO as GPIO


class Daylight:
    DAWN_PIN = 24
    DUSK_PIN = 25


    def __init__():
        GPIO.setup(DAWN_PIN, GPIO.OUT)
        GPIO.setup(DUSK_PIN, GPIO.OUT)


    def dawn():
        GPIO.setup(DAWN_PIN, GPIO.OUT)
    

    def dust():
        GPIO.setup(DUST_PIN, GPIO.OUT)
