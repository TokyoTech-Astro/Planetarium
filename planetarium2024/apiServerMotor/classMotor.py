

class Motor(Thread):
    def __init__(self,pins,dir,deg,speed):
        super(Motor,self).__init__()
        self.pins = [
            DigitalOutputDevice(21),
            DigitalOutputDevice(12),
            DigitalOutputDevice(8),
            DigitalOutputDevice(23)
        ]
        self.dir = dir
        self.deg = deg
        self.steps = deg*5
        self.speed = speed

    def run(self):
        print(f'Rotation dir={self.dir} deg={self.deg} speed={self.speed}')
        self.rotate()

    def set(self,dir,deg,speed):
        self.dir = dir
        self.deg = deg
        self.steps = deg*5
        self.speed = speed

    def rotate(self):        
        while self.steps > 0:
            self.steps-=1

            if self.speed == "low":
                sleepTime = 0.012
            elif self.speed == "medium":
                sleepTime = 0.006
            elif self.speed == "high":
                sleepTime = 0.003
            else:
                return
            
            if self.dir == "forward":
                self.pins[0].on()
                self.pins[1].on()
                self.pins[2].off()
                self.pins[3].off()
                time.sleep(sleepTime)

                self.pins[0].off()
                self.pins[1].on()
                self.pins[2].on()
                self.pins[3].off()
                time.sleep(sleepTime)

                self.pins[0].off()
                self.pins[1].off()
                self.pins[2].on()
                self.pins[3].on()
                time.sleep(sleepTime)

                self.pins[0].on()
                self.pins[1].off()
                self.pins[2].off()
                self.pins[3].on()
                time.sleep(sleepTime)
            
            elif self.dir == "back":
                self.pins[0].on()
                self.pins[1].on()
                self.pins[2].off()
                self.pins[3].off()
                time.sleep(sleepTime)

                self.pins[0].on()
                self.pins[1].off()
                self.pins[2].off()
                self.pins[3].on()
                time.sleep(sleepTime)

                self.pins[0].off()
                self.pins[1].off()
                self.pins[2].on()
                self.pins[3].on()
                time.sleep(sleepTime)

                self.pins[0].off()
                self.pins[1].on()
                self.pins[2].on()
                self.pins[3].off()
                time.sleep(sleepTime)

            else:
                return