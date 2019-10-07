import RPi.GPIO as GPIO
from gpio_maintaner import GPIOMaintainer

starpicturesPin = [5,6,7,8,9,11,12,13,16,21]
starpicturesName = ["おうし","おおいぬ","やぎ","しし","エリダヌス","かに","ぎょしゃ","ふたご","こいぬ","オリオン"]

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
    elif abs(pin) == 3:
        if pin > 0:
            print("GPIO 3 (恒星) on")
            GPIO.output(pin,1)
        else:
            print("GPIO 3 (恒星) off")
            GPIO.output(-pin,0)
    elif abs(pin) == 2:
        if pin > 0:
            print("GPIO 2 (一等星) on")
            GPIO.output(pin,1)
        else:
            print("GPIO 2 (一等星) off")
            GPIO.output(-pin,0)
    else:
        print("Error:PinNumber is over the management pin.")



if __name__ == "__main__":
    with GPIOMaintainer():
        while True:
            pin = input("Please enter the pin number or exit")
            if pin == "exit":
                break
            else:
                GPIOswitch(int(pin))