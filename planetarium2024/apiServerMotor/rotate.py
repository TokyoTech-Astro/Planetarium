from gpiozero import DigitalOutputDevice
import time
import sys

def rotate(dir:str, deg:int, speed:str):
    clk = DigitalOutputDevice(15)
    cw_ccw = DigitalOutputDevice(18)
    sleep_ref = DigitalOutputDevice(23)
    vdd = DigitalOutputDevice(24)

    if dir == "forward":
        cw_ccw.on()
    elif dir == "back":
        cw_ccw.off()
    else:
        return

    if speed == "low":
        period = 0.008
    elif speed == "medium":
        period = 0.005
    elif speed == "high":
        period = 0.003
    else:
        return
    
    sleep_ref.on()
    vdd.on()
    
    for _ in range(deg*60):
        clk.on()
        time.sleep(period/2)
        clk.off()
        time.sleep(period/2)
    
if __name__ == "__main__":
    dir = sys.argv[1]
    deg = int(float(sys.argv[2]))
    speed = sys.argv[3]
    rotate(dir,deg,speed)