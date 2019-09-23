import time
import RPi.GPIO as GPIO
from switch import GPIOswitch


FIXEDSTAR_PIN = 12


def Automode_S(sc):

    print("AutoMode_S")
    while True:
        mode = sc.receivedata()
        if mode == "fixedstar":
            print("fixedstsar")
            GPIOswitch(FIXEDSTAR_PIN)
        elif mode == "starpicture":
            while True:
                pin = sc.receivedata()
                if pin == "end":
                    break
                else:
                    GPIOswitch(abs(int(pin)))
            print("end starpicture")
        
        elif mode == "exit":
            break
        else:
            print("Error")
            time.sleep(0.5)
