import socket
import time
import RPi.GPIO as GPIO
from gpio_maintaner import GPIOMaintainer
from StepperMotor import StepperMotor
from threading import Thread
import threading
from AutoMode_C import Automode_C
from daylight import Daylight


#import pygame
from Audio import Audio

Port = 50007
IP = '192.168.11.2'
ip = '192.168.0.11'

stepping = 0
continuing = True

class SocketCommunication_C():

    def __init__(self,s):
        self.port = Port
        self.ip = ip
        self.s = s

        
    def setup(self):
        self.s.connect((self.ip, self.port))
        print("Connected")

    def senddata(self,string):
        self.s.sendall(string.encode())
    
    def receivedata(self):
        return self.s.recv(1024).decode()

    def __exit__(self, type, value, traceback):
        pass


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
                if stepping % 50 == 0:
                    print("STEPPER: {}".format(stepping))
                self.stepper.fRotate(1)
                stepping -= 1
            elif stepping < 0:
                if stepping % 50 == 0:
                    print("STEPPER: {}".format(stepping))
                self.stepper.rRotate(1)
                stepping += 1



if __name__ == "__main__":
    with GPIOMaintainer():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            sc = SocketCommunication_C(s)
            sc.setup()
            with Daylight() as dl, StepperMotor(0.004) as sm:
                while True:
                    print("Please enter the mode in server")
                    mode = sc.receivedata()
                    if mode == "audio":
                        name = sc.receivedata()
                        Audio(name).start()
                    elif mode == "motor":
                        continuing = True
                        StepperService(sm).start()
                        stepping += int(sc.receivedata())
                    elif mode == "daylight":
                        onoff = sc.receivedata()
                        if onoff == "on":
                            dl.dawn()
                        elif onoff == "off":
                            dl.dusk()
                        else:
                            print("Error")

                    elif mode == "auto":
                        continuing = True
                        Automode_C("K2019.json",sc,dl,sm)
                    
                    elif mode == "exit":
                        print("exit")
                        continuing = False
                        break
                    
                    else:
                        print("Error")
                        time.sleep(0.5)

                        


                






