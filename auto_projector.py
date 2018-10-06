from threading import Thread
import threading
import os
import time
import sys
import json
from pydub import AudioSegment
from pydub.playback import play
from gpio_maintaner import GPIOMaintainer
from starsphere import StarSphere
from shooting_star import ShootingStar
from stepper_motor import StepperMotor
from daylight import Daylight


FIXED_STAR = 4
MP3_DIR = os.environ["PLAN_MP3_DIR"]


class NotIncludingIntervalException(Exception):
    def __init__(self, num):
        self.message = "{}番目のシーケンス要素にintervalが設定されていません".format(num + 1)


stepping = 0
continuing = True


class StepperService(Thread):
    def __init__(self):
        super(StepperService, self).__init__()


    def run(self):
        with StepperMotor(0.004) as step:
            global stepping
            while continuing or not stepping == 0:
                if stepping == None:
                    break
                elif stepping > 0:
                    print("STEPPER: {}".format(stepping))
                    step.rRotate(1)
                    stepping -= 1
                elif stepping < 0:
                    print("STEPPER: {}".format(stepping))
                    step.fRotate(1)
                    stepping += 1


class AudioTask(Thread):
    def __init__(self, path):
        super().__init__()
        self.stop_event = threading.Event()
        self.path = path
        self.thread = threading.Thread(target = self.play)
        self.thread.start()


    def play(self):
        play(AudioSegment.from_mp3(self.path))


def testSeq(seq):
    for i, e in enumerate(seq):
        if "interval" not in e:
            raise NotIncludingIntervalException(i)


def auto_project(path):
    seq = None
    with open(path) as f:
        seq = json.load(f)
    testSeq(seq)
    with GPIOMaintainer():
        with StarSphere(os.environ["PLAN_SERVER_IP"], int(os.environ["PLAN_SERVER_PORT"])) as ss:
            with Daylight() as dl:
                shoot = ShootingStar()
                service = StepperService()
                service.start()
                for e in seq:
                    print(e)
                    if e["interval"] == "wait":
                        while True:
                            if stepping == 0:
                                break
                            time.sleep(0.03)
                    elif e["interval"] == "force":
                        stepping = 0
                    else:
                        time.sleep(e["interval"])
                    print("i slept well")
                    if e.get("daylight") != None:
                        if e["daylight"]:
                            dl.dawn()
                        else:
                            dl.dusk()
                    if e.get("shootingstar") != None:
                        if e["shootingstar"]:
                            shoot.start()
                        else:
                            shoot.stop()
                    if e.get("fixedstar") != None:
                        ss.toggleSwitch(e["fixedstar"], FIXED_STAR)
                    if e.get("picture") != None:
                        for f in e["picture"]:
                            ss.toggleSwitch(f > 0, abs(f))
                    if e.get("audio") != None:
                        AudioTask(MP3_DIR + e["audio"] + ".mp3")
                    if e.get("stepper") != None:
                        stepping += e["stepper"]
                continuing = False
                service.join()




if __name__ == "__main__":
    auto_project(sys.argv[1])
    