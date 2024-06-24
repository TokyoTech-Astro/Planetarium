from gpiozero import DigitalOutputDevice
import time
import sys

def rotate(dir:str, deg:int, speed:str):
    pins = [
        DigitalOutputDevice(21),
        DigitalOutputDevice(12),
        DigitalOutputDevice(8),
        DigitalOutputDevice(23)
    ]

    if speed == "low":
        sleepTime = 0.012
    elif speed == "medium":
        sleepTime = 0.006
    elif speed == "high":
        sleepTime = 0.003
    else:
        return
            
    if dir == "forward":
        for _ in range(deg*5):
            pins[0].on()
            pins[1].on()
            pins[2].off()
            pins[3].off()
            time.sleep(sleepTime)
            pins[0].off()
            pins[1].on()
            pins[2].on()
            pins[3].off()
            time.sleep(sleepTime)
            pins[0].off()
            pins[1].off()
            pins[2].on()
            pins[3].on()
            time.sleep(sleepTime)
            pins[0].on()
            pins[1].off()
            pins[2].off()
            pins[3].on()
            time.sleep(sleepTime)
            
    elif dir == "back":
        for _ in range(5*deg):
            pins[0].on()
            pins[1].on()
            pins[2].off()
            pins[3].off()
            time.sleep(sleepTime)
            pins[0].on()
            pins[1].off()
            pins[2].off()
            pins[3].on()
            time.sleep(sleepTime)
            pins[0].off()
            pins[1].off()
            pins[2].on()
            pins[3].on()
            time.sleep(sleepTime)
            pins[0].off()
            pins[1].on()
            pins[2].on()
            pins[3].off()
            time.sleep(sleepTime)
    
if __name__ == "__main__":
    dir = sys.argv[1]
    deg = int(float(sys.argv[2]))
    speed = sys.argv[3]
    rotate(dir,deg,speed)