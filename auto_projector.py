import threading
import time
import sys
import json
import gpio_controller
from gpio_maintaner import GPIOMaintainer
from starsphere import StarSphere
from shooting_star import ShootingStar
from stepper_motor import StepperMotor
from daylight import Daylight


ADDRESS = ""
PORT = ""
FIXED_STAR = 0


class NotIncludingIntervalException(Exception):
    def __init__(self, num):
        self.message = "{}番目のシーケンス要素にintervalが設定されていません".format(num + 1)


def testSeq(seq):
    for i, e in seq:
        if "interval" not in e:
            raise NotIncludingIntervalException(i)
            break


if __name__ == "__main__":
    seq = None
    # with open("") as f:
    #     seq = json.load(f)
    # testSeq(seq)
    with GPIOMaintainer() as m:
        dl = Daylight(m.queue)
        shoot = ShootingStar(m.queue)
        step = StepperMotor(0.004, m.queue)
        ss = StarSphere(ADDRESS, PORT)
        
        for e in seq:
            if e.get("daylight") != None:
                if e["daylight"]:
                    threading.Thread(target=dl.dawn()).start()
                else:
                    threading.Thread(target=dl.dust()).start()
            if e.get("shootingstar") != None:
                if e["shootingstar"]:
                    shoot.start()
                else:
                    shoot.stop()
            if e.get("fixedstar") != None:
                ss.toggleSwitch(e["fixedstar"], FIXED_STAR)
            if e.get("stepper") != None:
                if e.get("stepper")

                

            time.sleep(int(e["interval"]))


        
