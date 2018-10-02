import threading
import queue
import time
import os
import ConfigParser
import RPi.GPIO as GPIO

import server


class Task:
    def __init__(self, mode: bool, pin: int):
        self.mode = mode
        self.pin = pin


CONFIG_PATH = "./setting.ini"

q = queue.Queue()
finished = False
if not os.path.isfile(CONFIG_PATH):
    print("GENERATING A SETTING FILE...")
    with open(CONFIG_PATH, "w") as f:
        f.write("[PinMap]")
        for i in range(2,27):
            f.wirte("{} = ".format(i))
            f.write("\n")

config = ConfigParser.ConfigParser()
config.read()
pinmap = [0 for i in range(27)]
for i in range(2, 27):
    res = int(config.get("PinMap", str(i)))
    print("S {server} -> {reciever} R".format(server=i, reciever=res))
    pinmap[i] = res


def socketService(conn):
    task = q.get()
    if finished:
        sendExit()
        return False
    sendCode(task.mode, task.pin)
    return True


def controllerService():
    GPIO.setmode(GPIO.BCM)
    for i in range(2, 27):
        GPIO.setup(i, GPIO.IN)
        GPIO.add_event_detect(i, GPIO.RISING, callback=lambda x: q.put(True, pinmap[i]), bouncetime=200)
        GPIO.add_event_detect(i, GPIO.FALLING, callback=lambda x: q.put(False, pinmap[i]), bouncetime=200)
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        GPIO.cleanup()
        finished = True


if __name__ == '__main__':
    threading.Thread(target=communicate, args=(socketService), name="Socket Server Thread").start()
    threading.Thread(target=controllerService, name="Control Service Thread").start()
