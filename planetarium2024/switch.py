# -*- coding: utf-8 -*-
import sys
import RPi.GPIO as GPIO
from gpio_maintaner import GPIOMaintainer

starpicturesPin = [9,11,5,13,19,26,25,8,7,12,20,21]
starpicturesName = ["さそり座","ペガサス","おおいぬ","こいぬ","こぐま","オリオン","none","none","none","none","none","いて"]

def GPIOswitch(pin):
    #pin:int
    
    GPIO.setup(abs(pin),GPIO.OUT)
    if abs(pin) in starpicturesPin:
        Starpicture = starpicturesName[starpicturesPin.index(abs(pin))]
        if pin > 0:
            print("GPIO {0} ({1}座) on".format(str(abs(pin)),Starpicture))
            GPIO.output(pin,1)
        else:
            print("GPIO {0} ({1}座) off".format(str(abs(pin)),Starpicture))
            GPIO.output(-pin,0)
    elif abs(pin) == 4:
        if pin > 0:
            print("GPIO 4 (恒星) on")
            GPIO.output(pin,0)
        else:
            print("GPIO 4 (恒星) off")
            GPIO.output(-pin,1)
    elif abs(pin) == 14:
        if pin > 0:
            print("GPIO 14 (一等星) on")
            GPIO.output(pin,1)
        else:
            print("GPIO 14 (一等星) off")
            GPIO.output(-pin,0)
    else:
        print("Error:PinNumber is over the management pin.")



if __name__ == "__main__":
    with GPIOMaintainer():
        if len(sys.argv) == 1:
            while True:
                pin = input("Please enter the pin number or exit")
                if pin == "exit":
                    break
                else:
                    GPIOswitch(int(pin))
        else:
            GPIOswitch(int(sys.argv[1]))
