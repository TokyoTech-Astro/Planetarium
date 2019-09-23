from threading import Thread
import threading
import time
import json
import RPi.GPIO as GPIO



stepping = 0
continuing = True


class StepperService(Thread):
    def __init__(self, stepper):
        super().__init__()
        self.stepper = stepper
        #stepper = StepperMoter


    def run(self):
        print("StepperService start")
        global stepping
        while continuing or not stepping == 0:
            if stepping == None:
                break
            elif stepping > 0:
                if stepping % 50 == 0:
                    print("STEPPER = " + str(stepping))
                self.stepper.fRotate(1)
                stepping -= 1
            elif stepping < 0:
                if stepping % 50 == 0:
                    print("STEPPER = " + str(stepping))
                self.stepper.rRotate(1)
                stepping += 1



#json
#socket communication
#daylight
#stepper moter

def Automode_C(js,sc,dl,sm):
    print("AutoMode")
    global stepping
    global continuing
    with open(js) as f:
        sequence = json.load(f)
    
    StepperService(sm).start()

    for i in sequence:
        if i.get("fixedstar") != None:
            sc.senddata("fixedstar")
        if i.get("daylight") != None:
            if i.get("daylight"):
                dl.dawn()
            else:
                dl.dusk() 
        if i.get("starpicture") != None:
            sc.senddata("starpicture")
            print(i["starpicture"])
            for pin in i["starpicture"]:  
                sc.senddata(str(pin))
                time.sleep(0.05)
            sc.senddata("end")
        if i.get("motor") != None: 
            stepping += i["motor"] 
        
        if i["interval"] == "wait":
            while True:
                if stepping == 0:
                    break
                time.sleep(0.05)
        elif i["interval"] == "end":
            continuing = False
            sc.senddata("exit")
            time.sleep(2)
            
        else:
            time.sleep(i["interval"])
        
    