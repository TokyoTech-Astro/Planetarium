import subprocess

class Motor:
    def __init__(self):
        self.proc = subprocess.Popen(":", shell=True)
        self.dir = None
        self.deg = None
        self.speed = None

    def rotate(self, dir:str, deg:int, speed:str):
        if self.proc.returncode == None:
            self.proc.terminate()
        self.proc = subprocess.Popen(["python", "rotate.py", dir, str(deg), speed])
        self.dir = dir
        self.deg = deg
        self.speed = speed

    def stop(self):
        if self.proc.returncode == None:
            self.proc.terminate()