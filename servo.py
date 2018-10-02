import time
import RPi.GPIO as GPIO


H = GPIO.HIGH
L = GPIO.LOW


def rRotate(step, t):
    for i in range(step):
        GPIO.output(4, H)
        GPIO.output(17, L)
        GPIO.output(27, L)
        GPIO.output(22, H)
        time.sleep(t)

        GPIO.output(4, L)
        GPIO.output(17, L)
        GPIO.output(27, H)
        GPIO.output(22, H)
        time.sleep(t)

        GPIO.output(4, L)
        GPIO.output(17, H)
        GPIO.output(27, H)
        GPIO.output(22, L)
        time.sleep(t)

        GPIO.output(4, H)
        GPIO.output(17, H)
        GPIO.output(27, L)
        GPIO.output(22, L)
        time.sleep(t)


def fRotate(step, t):
    for i in range(step):
        GPIO.output(4, H)
        GPIO.output(17, H)
        GPIO.output(27, L)
        GPIO.output(22, L)
        time.sleep(t)

        GPIO.output(4, L)
        GPIO.output(17, H)
        GPIO.output(27, H)
        GPIO.output(22, L)
        time.sleep(t)

        GPIO.output(4, L)
        GPIO.output(17, L)
        GPIO.output(27, H)
        GPIO.output(22, H)
        time.sleep(t)

        GPIO.output(4, H)
        GPIO.output(17, L)
        GPIO.output(27, L)
        GPIO.output(22, H)
        time.sleep(t)


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT)
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(27, GPIO.OUT)
    GPIO.setup(22, GPIO.OUT)


    for i in range(180):
        rRotate(1, 0)

    GPIO.cleanup()
