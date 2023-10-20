import time
import RPi.GPIO as GPIO
from switch import GPIOswitch

def Automode_S(sc):
    print("AutoMode_S")
    while True:
        inp = sc.receivedata()
        try:
            pin = int(inp)
            if abs(pin) <= 27:
                GPIOswitch(int(inp))
            else:
                print("The pin number does not exist.")
        except:
            if inp == "exit":
                print("Automode_S end")
                break
            else:
                break