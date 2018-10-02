import time
import RPi.GPIO as GPIO


H = GPIO.HIGH
L = GPIO.LOW

# 4, 17, 27, 22

class StepperMotor:
    def __init__(self, pMode, p1, p2, p3, p4, t):
        self.pMode = pMode
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.t = t


    def setInterval(self, t):
        self.t = t
        
    
    def __enter__(self):
        GPIO.setmode(self.pMode)
        GPIO.setup(self.p1, GPIO.OUT)
        GPIO.setup(self.p2, GPIO.OUT)
        GPIO.setup(self.p3, GPIO.OUT)
        GPIO.setup(self.p4, GPIO.OUT)

    
    def __exit__(self):
        GPIO.cleanup()
    

    def rRotate(self, step):
        for i in range(step):
            GPIO.output(self.p1, H)
            GPIO.output(self.p2, L)
            GPIO.output(self.p3, L)
            GPIO.output(self.p4, H)
            time.sleep(self.t)

            GPIO.output(self.p1, L)
            GPIO.output(self.p2, L)
            GPIO.output(self.p3, H)
            GPIO.output(self.p4, H)
            time.sleep(self.t)

            GPIO.output(self.p1, L)
            GPIO.output(self.p2, H)
            GPIO.output(self.p3, H)
            GPIO.output(self.p4, L)
            time.sleep(self.t)

            GPIO.output(self.p1, H)
            GPIO.output(self.p2, H)
            GPIO.output(self.p3, L)
            GPIO.output(self.p4, L)
            time.sleep(self.t)


    def fRotate(self, step):
        for i in range(step):
            GPIO.output(self.p1, H)
            GPIO.output(self.p2, H)
            GPIO.output(self.p3, L)
            GPIO.output(self.p4, L)
            time.sleep(self.t)

            GPIO.output(self.p1, L)
            GPIO.output(self.p2, H)
            GPIO.output(self.p3, H)
            GPIO.output(self.p4, L)
            time.sleep(self.t)

            GPIO.output(self.p1, L)
            GPIO.output(self.p2, L)
            GPIO.output(self.p3, H)
            GPIO.output(self.p4, H)
            time.sleep(self.t)

            GPIO.output(self.p1, H)
            GPIO.output(self.p2, L)
            GPIO.output(self.p3, L)
            GPIO.output(self.p4, H)
            time.sleep(self.t)

if __name__ == "__main__":
    with StepperMotor(GPIO.BCM, 4, 17, 27, 22, 0.004) as m:
        m.rRotate(1200)
