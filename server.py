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


    def toggleSwitch(self, toggle, port):
        value = 0
        if toggle:
            value = 0b10000000
        value += port
        self.sendCode(value)

    
    def sendExit(self):
        send(conn, 0b01111111)



def sendStr(conn, msg, enc=ENCODE):
    conn.send(msg.encode(encoding=enc))


def recieveStr(conn, enc=ENCODE, size=1024):
    return conn.recv(size).decode(encoding=enc)


def send(conn, value):
    conn.send(value.to_bytes(1, 'big'))


def recieve(conn, size=1):
    return int.from_bytes(conn.recv(size), 'big')


def sendExit(conn):
    send(conn, 0b01111111)


def sendCode(conn, toggle, port):
    value = 0
    if toggle:
        value = 0b10000000
    value += port
    send(conn, value)


def communicate(service):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 25565))
        s.listen(1)
        print("LISTENING NOW...")
        while True:
            conn, addr = s.accept()
            print("CONNECTED TO {}.".format(addr))
            with conn:
                try:
                    while service(conn):
                        res = recieve(conn)
                        if res != 0:
                            print("FAILED")
                            raise Exception
                        print("SUCCESS")
                except Exception as e:
                    sendExit(conn)
                    print(e)
                    break
    print("EXITING NOW...")


def defaultService(conn):
    inp = input("On, off or exit? :")
    while True:
        if "exit" in inp.lower():
            sendExit(conn)
            return False
        t = True
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
        sendCode(conn, t, pin)
        return True


if __name__ == '__main__':
    communicate(defaultService)
        