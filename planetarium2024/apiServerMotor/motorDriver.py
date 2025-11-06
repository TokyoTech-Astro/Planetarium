import subprocess

class Motor:
    def __init__(self):
        self.proc = subprocess.Popen(":", shell=True)
        self.dir = None
        self.deg = None
        self.time = None

    def rotate(self, dir:str, deg:int, time:float):
        if self.proc.returncode == None:
            self.proc.terminate()
        self.proc = subprocess.Popen(["python", "rotate.py", dir, str(deg), str(time)])
        self.dir = dir
        self.deg = deg
        self.time = time

    def stop(self):
        if self.proc.returncode == None:
            self.proc.terminate()