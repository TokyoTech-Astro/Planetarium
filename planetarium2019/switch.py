import RPi.GPIO as GPIO

def GPIOswitch(pin):
    #pin:int
    GPIO.setup(pin, GPIO.IN)
    if GPIO.input(pin) != 0:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,1)
    else:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,0)