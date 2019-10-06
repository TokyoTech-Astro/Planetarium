from threading import Thread
import threading
import time
import json
import RPi.GPIO as GPIO
from Audio import Audio


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

allstarsPin = [2,3,5,6,7,8,9,11,12,13,16,21]
allstarsName = ["一等星","恒星","おうし","おおいぬ","やぎ","しし","エリダヌス","かに","ぎょしゃ","ふたご","こいぬ","オリオン"]

def Automode_C(js,sc,dl,sm):
    print("AutoMode_C")
    switchCount = 0
    global stepping
    global continuing
    with open(js) as f:
        sequence = json.load(f)
    
    StepperService(sm).start()
    for i in sequence:
        if i.get("star") != None:
            for pin in i["star"]:   
                sc.senddata(str(pin))
                time.sleep(0.05)
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
            
            time.sleep(i["interval"] - 0.06*switchCount)
            switchCount = 0

    
    print("Automode_C end")
        
    