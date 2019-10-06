import time
import RPi.GPIO as GPIO
from switch import GPIOswitch

def Automode_S(sc):
    print("AutoMode_S")
    while True:
        inp = sc.receivedata()
        
        if inp == "exit":
            print("Automode_S end")
            break
        elif -40 <= int(inp) and int(inp) <= 40:
            GPIOswitch(int(inp))
        else:
            break