# -*- coding: utf-8 -*-
from threading import Thread
import threading
import time
import json
import RPi.GPIO as GPIO
from Audio import Audio
from StepperMotor import StepperMotor


stepping = 0
continuing = True

class StepperService(Thread):
    def __init__(self, stepper):
        super().__init__()
        self.stepper = stepper
        #stepper = StepperMoter


    def run(self):
        global stepping
        global continuing
        while continuing or not stepping == 0:
            if stepping == None:
                break
            elif stepping > 0:
                if stepping % 10 == 0:
                    print("STEPPER = " + str(stepping))
                self.stepper.fRotate(1)
                stepping -= 1
            elif stepping < 0:
                if stepping % 10 == 0:
                    print("STEPPER = " + str(stepping))
                self.stepper.rRotate(1)
                stepping += 1



#json
#socket communication
#daylight
#stepper moter

allstarsPin = [14,4,9,11,5,13,19,26,25,8,7,12,20,21]
allstarsName = ["一等星","恒星","さそり","ペガサス","おおいぬ","こいぬ","こぐま","オリオン","none","none","none","none","none","いて"]

def Automode_C(js,sc,dl):
    print("AutoMode_C")
    with StepperMotor(0.005) as smFront:
        switchCount = 0
        motorCount = 0
        global stepping
        global continuing
        with open(js) as f:
            sequence = json.load(f)
        
        StepperService(smFront).start()
        for i in sequence:
            if i.get("star") != None:
                for pin in i["star"]:   
                    sc.senddata(str(pin))
                    time.sleep(0.08)
            if i.get("daylight") != None:
                if i.get("daylight"):
                    dl.dawn()
                else:
                    dl.dusk() 
            if i.get("audio") != None:
                name = i.get("audio")
                Audio(name).start()

            if i.get("motor") != None: 
                stepping += i["motor"] 
                motorCount += i["motor"]
            
            if i["interval"] == "wait":
                while True:
                    if stepping == 0:
                        break
                    time.sleep(0.05)
            elif i["interval"] == "end":
                continuing = False

            else:    
                time.sleep(i["interval"] - 0.09*switchCount)
                switchCount = 0

    time.sleep(1)

    with StepperMotor(0.005) as smRear:
        StepperService(smRear).start()
        stepping += -motorCount
        sc.senddata("star")
        print("Turn off the all StarPins")
        for pin in allstarsPin:
            sc.senddata(str(-pin))
            sc.senddata(str(4))
            time.sleep(0.06)
        sc.senddata("exit")
        while True:
            if stepping == 0:
                continuing = False
                break
            time.sleep(0.03)
    sc.senddata("exit")
    print("Automode_C end\n")
        
    
