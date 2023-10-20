import socket
import time
import RPi.GPIO as GPIO
from gpio_maintaner import GPIOMaintainer
from StepperMotor import StepperMotor
from threading import Thread
import threading
from AutoMode_C import Automode_C
from daylight import Daylight
from switch import GPIOswitch
from Audio import Audio

Port = 50007
Destination = "pi-starsphere.local"
stepping = 0
continuing = True
allstarsPin = [2,3,5,6,7,8,9,11,12,13,16,21]
allstarsName = ["一等星","恒星","おうし","おおいぬ","やぎ","しし","エリダヌス","かに","ぎょしゃ","ふたご","こいぬ","オリオン"]
starpicturesPin = [5,6,7,8,9,11,12,13,16,21]
starpicturesName = ["おうし","おおいぬ","やぎ","しし","エリダヌス","かに","ぎょしゃ","ふたご","こいぬ","オリオン"]




class SocketCommunication_C():

    def __init__(self,s):
        self.port = Port
        self.dest = Destination
        self.s = s
        
    def setup(self):
        self.s.connect((self.dest, self.port))
        print("Connected")

    def senddata(self,string):
        self.s.sendall(string.encode())
    
    def receivedata(self):
        return self.s.recv(1024).decode()

    def __exit__(self, type, value, traceback):
        pass
        #self.conn.close()


class StepperService(Thread):
    def __init__(self, stepper):
        super().__init__()
        self.stepper = stepper


    def run(self):
        global stepping
        while continuing or stepping != 0:
            
            if stepping == None:
                break
            elif stepping > 0:
                if stepping % 10 == 0:
                    print("STEPPER: {}".format(stepping))
                self.stepper.fRotate(1)
                stepping -= 1
            elif stepping < 0:
                if stepping % 10 == 0:
                    print("STEPPER: {}".format(stepping))
                self.stepper.rRotate(1)
                stepping += 1

def AutoModeReset(step):
    global stepping
    global continuing
    continuing = True
    #GPIO.setmode(GPIO.BCM)
    
                                
    
    sc.senddata("star")
    print("Turn off the all StarPins")
    for pin in allstarsPin:
        sc.senddata(str(-pin))
        time.sleep(0.06)
    sc.senddata("exit")



if __name__ == "__main__":
    with GPIOMaintainer():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            sc = SocketCommunication_C(s)
            sc.setup()
            with Daylight() as dl:
                while True:             
                    mode = input("StarAllOf => all\nSwitching star => star\nPlaying audio =>audio\nRotation motor =>motor\nSwitching daylight => daylight\nAutomode => auto\nExit => exit\n\n")
                    if mode == "all":
                        sc.senddata("star")
                        print("Turn off the all StarPins")
                        for pin in allstarsPin:
                            sc.senddata(str(-pin))
                            time.sleep(0.06)
                        sc.senddata("exit")
                    elif mode == "star":
                        sc.senddata("star")
                        for i in range(len(allstarsName)):
                            print("{0} => {1}".format(allstarsName[i],allstarsPin[i]))
                        print("StarpictureAllOn => allon\nStarpictureAllOff => alloff\nExit => exit\n")
                        while True: 
                            inp = input()
                            try:
                                pin = int(inp)
                                if -40 <= pin and pin <= 40:
                                    sc.senddata(inp)
                                else:
                                    print("The pin number does not exist.")
                            except:
                                if inp == "exit":
                                    sc.senddata("exit")
                                    print()
                                    break
                                elif inp == "allon":
                                    for pin in starpicturesPin:
                                        sc.senddata(str(pin))
                                        time.sleep(0.06)
                                elif inp == "alloff":
                                    for pin in starpicturesPin:
                                        sc.senddata(str(-pin))
                                        time.sleep(0.06)
                                else:
                                    print("Please enter the correct string/integer.")

                    elif mode == "audio":
                        #name = input("Please enter the music name")
                        Audio("K2019").start()

                    elif mode == "motor":
                        continuing = True
                        inp = input("Please enter the speed")
                        try:
                            with StepperMotor(abs(float(inp))) as sm:
                                inp = input("Please enter the stepping number")
                                try:
                                    stepping += int(inp)
                                    StepperService(sm).start()
                                    while True:
                                        if stepping == 0:
                                            continuing = False
                                            break
                                        time.sleep(0.03)
                                except:
                                    print("Please enter the integer")
                        except:
                            print("Please enter the integer")
                
                    elif mode == "daylight":
                        inp = input("On => on\nOff => off\n")
                        if inp == "on":
                            dl.dawn()
                        elif inp == "off":
                            dl.dusk()
                        else:
                            print("Please enter on or off ")

                    elif mode == "auto":
                        continuing = True
                        
                        sc.senddata("auto")
                        Automode_C("K2023.json",sc,dl)

                        
                                            
                    elif mode == "exit":
                        print("exit")
                        sc.senddata("exit")
                        continuing = False
                        break

                    else:
                        print("Please enter the correct string.")
                            


                






