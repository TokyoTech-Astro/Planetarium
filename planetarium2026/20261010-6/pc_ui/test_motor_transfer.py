import time
import tkinter as tk
import unittest
from app import App, MotorTransferWindow

class FakeApp:
    frame=App.frame
    label=App.label
    button=App.button
    def __init__(self,root):
        self.root=root;self.actual={'angle':270.0,'speed':0.0};self.motor_motion='stopped'
        self.last_motor_status=0;self.motor_calibration_mode=False;self.emergency_stop=False
        self.commands=[];self.motor_transfer=None;self.played=False;self.pos=tk.DoubleVar(root)
    def actual_link_ok(self,_):return True
    def send_motor_calibration(self,action,speed=0,value=0):
        self.commands.append((action,speed,value));return True
    def apply_timeline(self,*_):pass
    def play(self):self.played=True

class TransferTest(unittest.TestCase):
    def setUp(self):self.root=tk.Tk();self.root.withdraw();self.app=FakeApp(self.root)
    def tearDown(self):self.root.destroy()
    def begin_move(self):
        window=MotorTransferWindow(self.app,-270,0,True);self.app.motor_transfer=window;window.w.withdraw()
        self.app.motor_calibration_mode=True;self.app.last_motor_status=time.monotonic()+.01
        window.update();return window
    def test_return_uses_reverse_path_and_waits_for_confirmation(self):
        window=self.begin_move()
        self.assertEqual(self.app.commands[0][0],'stop')
        self.assertEqual(self.app.commands[1],('move_relative',5.0,-270.0))
        self.assertFalse(self.app.played)
        self.app.actual['angle']=0;self.app.last_motor_status=window.started+1
        window.update();self.assertEqual(self.app.commands[-1][0],'exit')
        self.app.motor_calibration_mode=False;self.app.last_motor_status=window.exit_at+1
        window.update();self.assertTrue(self.app.played);self.assertIsNone(self.app.motor_transfer)
    def test_stop_does_not_resume_audio(self):
        window=self.begin_move();window.stop();window.update()
        self.assertEqual(self.app.commands[-1][0],'stop');self.assertFalse(window.resume)
        self.assertFalse(self.app.played)

if __name__=='__main__':unittest.main()
