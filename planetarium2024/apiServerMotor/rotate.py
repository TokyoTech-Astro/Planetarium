from gpiozero import DigitalOutputDevice
import time
import sys

n_divided = 1

def rotate(dir:str, deg:int, speed:str):
    clk = DigitalOutputDevice(22)
    cw_ccw = DigitalOutputDevice(27)
    sleep_ref = DigitalOutputDevice(17)
    vdd = DigitalOutputDevice(4)

    if dir == "forward":
        cw_ccw.on()
    elif dir == "back":
        cw_ccw.off()
    else:
        return

    if speed == "low":
        period = 0.016 / n_divided
    elif speed == "medium":
        period = 0.010 / n_divided
    elif speed == "high":
        period = 0.006 / n_divided
    else:
        return
    
    sleep_ref.on()
    vdd.on()
    
    for _ in range(deg*60*n_divided):
        clk.on()
        time.sleep(period/2)
        clk.off()
        time.sleep(period/2)
    
if __name__ == "__main__":
    dir = sys.argv[1]
    deg = int(float(sys.argv[2]))
    speed = sys.argv[3]
    rotate(dir,deg,speed)