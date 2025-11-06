from gpiozero import DigitalOutputDevice
import time
import sys

n_divided = 1

def rotate(dir:str, deg:int, rot_time:float):
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

    period = rot_time / (60.0 * deg)
    
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
    rot_time = float(sys.argv[3])
    rotate(dir, deg, rot_time)