import sys
import socket
from gpio_maintaner import GPIOMaintainer
import RPi.GPIO as GPIO


class GPIOMaintainerForServer(GPIOMaintainer):
    def __init__(self):
        GPIO.setmode(GPIO.BCM)


    def __enter__(self):
        for i in range(2, 27):
            GPIO.setup(i, GPIO.OUT)
        return self


    def __exit__(self, type, value, traceback):
        GPIO.cleanup()



class StarSphereServer:
    def __init__(self, port, listen):
        self.port = port
        self.listen = listen
        

    def sendCode(self, value):
        self.conn.send(value.to_bytes(1, 'big'))


    def recieveCode(self, size=1):
        return int.from_bytes(self.conn.recv(size), 'big')


    def serve(self):
        with GPIOMaintainerForServer():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', self.port))
                s.listen(self.listen)
                print("Waiting now...")
                while True:
                    conn, addr = s.accept()
                    self.conn = conn
                    print("Connecting to {}.".format(addr))
                    with conn:
                        try:
                            while True:
                                data = self.recieveCode()
                                print("Recieved data: {}".format(data))
                                if data == 0:
                                    print("Connection finished")
                                    break
                                if data & 0b10000000 == 0b10000000:
                                    pin = data ^ 0b10000000
                                    print("TURN ON: %d -> " % pin, end="")
                                    GPIO.output(pin, GPIO.HIGH)
                                    print("DONE")
                                elif data != 0b01111111:
                                    pin = data
                                    print("TURN OFF: %d -> " % pin)
                                    GPIO.output(pin, GPIO.LOW)
                                    print("DONE")
                                else:
                                    break
                                self.sendCode(0)
                        except ConnectionError as e:
                            print("Exception was thrown on connection.")
                            print(e)
                        except Exception as e:
                            print("Exception was thrown.")
                            print(e)
                            self.sendCode(1)
                            break


if __name__ == "__main__":
    StarSphereServer(25565, 1).serve()
