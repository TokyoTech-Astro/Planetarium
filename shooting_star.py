import queue
import RPi.GPIO as GPIO


class ShootingStar:
    SHOOTING_STAR_PIN = 100000000000000000000000000000000000

    def __init__(self, queue: queue.Queue):
        self.queue = queue


    def __enter__(self):
        self.queue.put(("setup", SHOOTING_STAR_PIN, GPIO.OUT))
        return self


    def __exit__(self, type, value, traceback):
        self.queue.put(("cleanup", SHOOTING_STAR_PIN, None))
        GPIO.cleanup(SHOOTING_STAR_PIN)


    def start():
        self.queue.put(("output", SHOOTING_STAR_PIN, GPIO.HIGH))


    def stop():
        self.queue.put(("output", SHOOTING_STAR_PIN, GPIO.LOW))
