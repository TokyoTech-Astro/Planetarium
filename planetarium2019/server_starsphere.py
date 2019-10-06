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
                try:
                    mode = sc.receivedata()
                except:
                    break
                if mode == "star":
                    while True:
                        inp = sc.receivedata()
                        if inp == "exit":
                            break
                        else:
                            GPIOswitch(int(inp))

                elif mode == "auto":
                    Automode_S(sc)
                
                elif mode == "exit":
                    break
                    
                else:
                    break

            
            
                



