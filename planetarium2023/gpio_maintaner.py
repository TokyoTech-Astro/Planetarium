import RPi.GPIO as GPIO

type = 0

class GPIOMaintainer:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)


    def __enter__(self):
        pass


    def __exit__(self, type, value, traceback):
        GPIO.cleanup()


if __name__ == "__main__":
    with GPIOMaintainer():
        print("GPIOMaintainer")

