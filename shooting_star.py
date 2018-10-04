import RPi.GPIO as GPIO


class ShootingStar:
    SHOOTING_STAR_PIN = 100000000000000000000000000000000000

    def __init__(self):
        pass


    def __enter__(self):
        GPIO.setup(SHOOTING_STAR_PIN, GPIO.OUT)
        return self


    def __exit__(self, type, value, traceback):
        GPIO.cleanup(SHOOTING_STAR_PIN)


    def start():
        GPIO.output(SHOOTING_STAR_PIN, GPIO.HIGH)


    def stop():
        GPIO.output(SHOOTING_STAR_PIN, GPIO.LOW)
