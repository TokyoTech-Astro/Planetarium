import socket
from threading import Thread
import time
import RPi.GPIO as GPIO
from gpio_maintaner import GPIOMaintainer
from AutoMode_S import Automode_S
from switch import GPIOswitch




#Server
Port = 50007

class SocketCommunication_S():
    def __init__(self,s):
        self.port = Port


    def setup(self):
        s.bind(('', self.port))
        s.listen(1)
        print("Waiting now...")
        conn, addr = s.accept()
        self.conn = conn
        print("Connecting to {}.".format(addr))

    def senddata(self,string):
        self.conn.sendall(string.encode())
    
    def receivedata(self):
        return self.conn.recv(1024).decode()
    
    def __exit__(self, type, value, traceback):
        self.conn.close()







if __name__ == "__main__":
    with GPIOMaintainer():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            sc = SocketCommunication_S(s)
            sc.setup()

            
            while True:
                mode = input("star, audio, motor, daylight, auto, exit\nPlease choose above\ninput = ")
                
                if mode == "star":
                    GPIOswitch(int(input("Please enter the pin number\nfixedstar:\n")))
                elif mode == "audio":
                    sc.senddata("audio")
                    inp_audio = input("Please enter the music name")
                    sc.senddata(inp_audio)
                elif mode == "motor":
                    sc.senddata("motor")
                    stepping = input("Please enter the stepping number")
                    sc.senddata(stepping)
                elif mode == "daylight":
                    sc.senddata("daylight")
                    sc.senddata(input("on or off"))
                elif mode == "auto":
                    sc.senddata("auto")
                    Automode_S(sc)
                elif mode == "exit":
                    sc.senddata("exit")
                    time.sleep(1)
                    break
                else:
                    print("Please enter the correct word.")
                



