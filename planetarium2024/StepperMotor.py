# -*- coding: utf-8 -*-
import sys
import time
import RPi.GPIO as GPIO
from gpio_maintaner import GPIOMaintainer


H = GPIO.HIGH
L = GPIO.LOW

# 21,12,8,23

class StepperMotor:
    def __init__(self, t, p1=21, p2=12, p3=8, p4=23):
        self.pin = [p1, p2, p3, p4]
        self.t = t


    def setInterval(self, t):
        self.t = t
    
    
    def __enter__(self):
        for i in range(4):
            GPIO.setup(self.pin[i], GPIO.OUT)
        self.off()
        return self

    
    def __exit__(self, type, value, traceback):
        pass


    def off(self):
        for i in range(4):
            GPIO.output(self.pin[i], H)
    

    #モーター型番：PK296A1-SG36
    #1step = 0.2度
    def rRotate(self, step):
        for _ in range(step):
            GPIO.output(self.pin[0], H)
            GPIO.output(self.pin[1], L)
            GPIO.output(self.pin[2], L)
            GPIO.output(self.pin[3], H)
            time.sleep(self.t)
            #0.05度

            GPIO.output(self.pin[0], L)
            GPIO.output(self.pin[1], L)
            GPIO.output(self.pin[2], H)
            GPIO.output(self.pin[3], H)
            time.sleep(self.t)

            GPIO.output(self.pin[0], L)
            GPIO.output(self.pin[1], H)
            GPIO.output(self.pin[2], H)
            GPIO.output(self.pin[3], L)
            time.sleep(self.t)

            GPIO.output(self.pin[0], H)
            GPIO.output(self.pin[1], H)
            GPIO.output(self.pin[2], L)
            GPIO.output(self.pin[3], L)
            time.sleep(self.t)
        self.off()


    def fRotate(self, step):
        for _ in range(step):
            GPIO.output(self.pin[0], H)
            GPIO.output(self.pin[1], H)
            GPIO.output(self.pin[2], L)
            GPIO.output(self.pin[3], L)
            time.sleep(self.t)

            GPIO.output(self.pin[0], L)
            GPIO.output(self.pin[1], H)
            GPIO.output(self.pin[2], H)
            GPIO.output(self.pin[3], L)
            time.sleep(self.t)

            GPIO.output(self.pin[0], L)
            GPIO.output(self.pin[1], L)
            GPIO.output(self.pin[2], H)
            GPIO.output(self.pin[3], H)
            time.sleep(self.t)

            GPIO.output(self.pin[0], H)
            GPIO.output(self.pin[1], L)
            GPIO.output(self.pin[2], L)
            GPIO.output(self.pin[3], H)
            time.sleep(self.t)
        self.off()


    def rRotateDeg(self, deg):
        step = int(3*int(deg)/0.2)
        for _ in range(step):
            GPIO.output(self.pin[0], H)
            GPIO.output(self.pin[1], L)
            GPIO.output(self.pin[2], L)
            GPIO.output(self.pin[3], H)
            time.sleep(self.t)

            GPIO.output(self.pin[0], L)
            GPIO.output(self.pin[1], L)
            GPIO.output(self.pin[2], H)
            GPIO.output(self.pin[3], H)
            time.sleep(self.t)

            GPIO.output(self.pin[0], L)
            GPIO.output(self.pin[1], H)
            GPIO.output(self.pin[2], H)
            GPIO.output(self.pin[3], L)
            time.sleep(self.t)

            GPIO.output(self.pin[0], H)
            GPIO.output(self.pin[1], H)
            GPIO.output(self.pin[2], L)
            GPIO.output(self.pin[3], L)
            time.sleep(self.t)
        self.off()


    def fRotateDeg(self, deg):
        step = int(3*int(deg)/0.2)
        for _ in range(step):
            GPIO.output(self.pin[0], H)
            GPIO.output(self.pin[1], H)
            GPIO.output(self.pin[2], L)
            GPIO.output(self.pin[3], L)
            time.sleep(self.t)

            GPIO.output(self.pin[0], L)
            GPIO.output(self.pin[1], H)
            GPIO.output(self.pin[2], H)
            GPIO.output(self.pin[3], L)
            time.sleep(self.t)

            GPIO.output(self.pin[0], L)
            GPIO.output(self.pin[1], L)
            GPIO.output(self.pin[2], H)
            GPIO.output(self.pin[3], H)
            time.sleep(self.t)

            GPIO.output(self.pin[0], H)
            GPIO.output(self.pin[1], L)
            GPIO.output(self.pin[2], L)
            GPIO.output(self.pin[3], H)
            time.sleep(self.t)
        self.off()




#if __name__ == "__main__":
#    with GPIOMaintainer():
#        with StepperMotor(0.005) as sm:
#            sm.rRotate(2700)
#        print("rot end")

if __name__ == "__main__":
    with GPIOMaintainer():
        if len(sys.argv) == 1:
            dire = input("input direction f or r:")
            rot = input("input rotation amount:")
            with StepperMotor(0.006) as sm:
                if dire=='f':
                    sm.fRotate(int(rot))
                    print("rot end")
                if dire=='r':
                    sm.rRotate(int(rot))
                    print("rot end")
        if len(sys.argv) == 3:
            dire = sys.argv[1]
            deg = sys.argv[2]
            with StepperMotor(0.006) as sm:
                if dire=='f':
                    sm.fRotateDeg(deg)
                    print("rot end")
                if dire=='r':
                    sm.rRotateDeg(deg)
                    print("rot end")
