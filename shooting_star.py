import RPi.GPIO as GPIO

SHOOTING_STAR_PIN = 100000000000000000000000000000000000


class ShootingStar:
    def __init__(self):
        pass


    def __enter__(self):
        GPIO.setup(SHOOTING_STAR_PIN, GPIO.OUT)
        return self


    def __exit__(self, type, value, traceback):
        GPIO.cleanup(SHOOTING_STAR_PIN)


    def start(self):
        GPIO.output(SHOOTING_STAR_PIN, GPIO.HIGH)


    def stop(self):
        GPIO.output(SHOOTING_STAR_PIN, GPIO.LOW)
