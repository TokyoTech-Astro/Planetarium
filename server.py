import sys
import socket

ENCODE = "utf-8"


class StarSphere:
    def __init__(self, address, port):
        self.destination = address
        self.port = port


    def __enter__(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.destination, self.port))
        return self


    def __exit__(self, type, value, traceback):
        self.conn.close()


    def sendCode(self, value):
        self.conn.sendall(value.to_bytes(1, 'big'))


    def recieveCode(self, size=1):
        return int.from_bytes(self.conn.recv(size), 'big')


    def toggleSwitch(self, toggle, pin):
        value = 0
        if toggle:
            value = 0b10000000
        value += pin
        self.sendCode(value)

    
    def sendExit(self):
        send(conn, 0b01111111)



def defaultService(ss: StarSphere):
    inp = input("On, off or exit? :")
    t = True
    while True:
        if "exit" in inp.lower():
            ss.sendExit
            return False
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
        except ValueError as e:
            print("Invalid value.")
            continue
        if pin > 128 or pin < 0:
            print("Invalid value.")
            continue
        ss.toggleSwitch(t, pin)
        return True


if __name__ == '__main__':
    with StarSphere("", 25565) as ss:
        print("Connected.")
        while defaultService(ss):
            if ss.recieveCode() != 0:
                print("Returned code is not zero.")
                break
