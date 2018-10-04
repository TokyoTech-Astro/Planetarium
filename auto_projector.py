from threading import Thread
import time
import sys
import json
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


stepping = False


class StepperTask(Thread):
    def __init__(self, ss: StepperMotor, step):
        self.ss = ss
        self.step = step
        pass


    def run(self):
        if not stepping:
            stepping = True
            if self.step > 0:
                ss.fRotate(step)
            else:
                ss.fRotate(-step)
        stepping = False



def testSeq(seq):
    for i, e in seq:
        if "interval" not in e:
            raise NotIncludingIntervalException(i)
            break



if __name__ == "__main__":
    seq = None
    with open("") as f:
        seq = json.load(f)
    testSeq(seq)
    with GPIOMaintainer():
        dl = Daylight()
        shoot = ShootingStar()
        step = StepperMotor(0.004)
        ss = StarSphere(ADDRESS, PORT)
        for e in seq:
            if e.get("daylight") != None:
                if e["daylight"]:
                    dl.dawn()
                else:
                    dl.dust()
            if e.get("shootingstar") != None:
                if e["shootingstar"]:
                    shoot.start()
                else:
                    shoot.stop()
            if e.get("fixedstar") != None:
                ss.toggleSwitch(e["fixedstar"], FIXED_STAR)
            if e.get("picture") != None:
                for f in e["picture"]:
                    ss.toggleSwitch(s < 0, abs(s))
            if e.get("stepper") != None:
                StepperTask(step, e["stepper"]).start()
            time.sleep(e["interval"])


        
