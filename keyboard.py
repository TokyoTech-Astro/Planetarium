import socket
from threading import Thread
from gpio_maintaner import GPIOMaintainer
from starsphere import StarSphere
from shooting_star import ShootingStar
from stepper_motor import StepperMotor
from daylight import Daylight


ADDRESS = "pi-starsphere.local"
PORT = 25565


stepping = 0


class StepperTask(Thread):
    def __init__(self, ss: StepperMotor):
        super(StepperTask, self).__init__()
        self.ss = ss
        pass


    def run(self):
        while True:
            if stepping == None:
                break
            elif stepping > 0:
                self.ss.rRotate(1)
            elif stepping < 0:
                self.ss.fRotate(1)


def stepperMotorHandler(m: StepperMotor):
    global stepping
    inp = input("f or r? :")
    while True:
        if "f" in inp.lower():
            stepping = -1
            break
        elif "r" in inp.lower():
            stepping = 1
            break
        else:
            print("Invalid value.")
    x = input("Press enter key to stop rotating.")
    stepping = 0
    return True


def shootingStarHandler(shoot: ShootingStar):
    inp = input("On or off? :")
    t = True
    while True:
        if "on" in inp.lower():
            break
        elif "off" in inp.lower():
            t = False
            break
        else:
            print("Invalid value.")
    if t:
        shoot.start()
    else:
        shoot.stop()
    return True


def daylightHandler(d: Daylight):
    inp = input("Dawn or dust? :")
    t = True
    while True:
        if "dawn" in inp.lower():
            break
        elif "dsut" in inp.lower():
            t = False
            break
        else:
            print("Invalid value.")
    if t:
        d.dawn()
    else:
        d.dusk()
    return True


def starSphereHandler(ss: StarSphere):
    inp = input("On or off? :")
    t = True
    while True:
        if "on" in inp.lower():
            break
        elif "off" in inp.lower():
            t = False
            break
        else:
            print("Invalid value.")
    while True:
        inp = input("Pin? :")
        pin = 0
        try:
            pin = int(inp)
        except ValueError:
            print("Invalid value.")
            continue
        if pin > 128 or pin < 0:
            print("Invalid value.")
            continue
        ss.toggleSwitch(t, pin)
        if ss.recieveCode != 0:
            print("Returned code is not zero.")
        return True


def command(inp: str, s: str):
    return s in inp.lower()


if __name__ == '__main__':
    with GPIOMaintainer():
        with StarSphere(ADDRESS, PORT) as ss:
            m = StepperMotor(0.004)
            shoot = ShootingStar()
            d = Daylight()
            StepperTask(StepperMotor(0.004)).start()
            res = True
            while res:
                inp = input("StarSphere => star\nShootingStar => shoot\nDaylight => day\nStepperMotor => motor\nExit => exit>")
                res = True
                if command(inp, "star"):
                    res = starSphereHandler(ss)
                elif command(inp, "shoot"):
                    res = shootingStarHandler(shoot)
                elif command(inp, "day"):
                    res = daylightHandler(d)
                elif command(inp, "motor"):
                    res = stepperMotorHandler(m)
                elif command(inp, "exit"):
                    res = False
            stepping = None
