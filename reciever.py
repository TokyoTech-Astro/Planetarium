import sys
import socket
import RPi.GPIO as GPIO


DESTINATION = "192.168.11.3"
ENCODE = "utf-8"


def sendStr(conn, msg, enc=ENCODE):
    conn.send(msg.encode(encoding=enc))


def recieveStr(conn, enc=ENCODE, size=1024):
    return conn.recv(size).decode(encoding=enc)


def send(conn, value):
    conn.sendall(value.to_bytes(1, 'big'))


def recieve(conn, size=1):
    return int.from_bytes(conn.recv(size), 'big')


GPIO.setmode(GPIO.BCM)
for i in range(2, 27):
    GPIO.setup(i, GPIO.OUT)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((DESTINATION, 25565))

    try:
        while True:
            data = recieve(s)
            print(data)
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
                GPIO.cleanup()
                break
            send(s, 0)
            print("send")
    except Exception as e:
        print("EXCEPTION WAS THROWN")
        print(e)
        GPIO.cleanup()
        send(s, 1)

print("EXITING NOW...")
