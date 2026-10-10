"""Check manual motor routing without opening a serial port or UI window."""
import unittest
from unittest.mock import patch

from app import App, FIELDS, defaults


class Variable:
    def __init__(self, value=False):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeApp:
    def __init__(self):
        self.root = None
        self.emergency_stop = False
        self.manual_motor_mode = False
        self.manual_motor_armed = False
        self.motor_origin_set = True
        self.motor_motion = "stopped"
        self.motor_playback_stopped = False
        self.playing = True
        self.calibration_window = None
        self.actual = defaults()
        self.actual["angle"] = 42.0
        self.desired = defaults()
        self.desired.update(angle=90.0, speed=3.0, first=True, p1=True)
        self.override = {key: Variable(False) for key in FIELDS}
        self.manual = {key: Variable("0" if key in ("angle", "speed") else "OFF") for key in FIELDS}
        self.auto = Variable(False)
        self.timeline = [dict(self.desired, time=0.0)]
        self.commands = []
        self.sent = []
        self.messages = []
        self.timeline_applied = []

    def actual_link_ok(self, device):
        return True

    def send_motor_calibration(self, action, speed=0.0, value=0.0):
        self.commands.append((action, speed, value))
        return True

    def send(self, force=False):
        self.sent.append((force, App.effective(self)))

    def apply_timeline(self, position, force=False):
        self.timeline_applied.append((position, force))
        self.send(True)

    def position(self):
        return 12.0

    def log(self, text):
        self.messages.append(text)

    def update_values(self):
        pass


class ManualMotorTests(unittest.TestCase):
    def test_start_keeps_light_timeline_and_suppresses_motor_target(self):
        app = FakeApp()
        for key in ("first", "stars", "p1"):
            app.override[key].set(True)
        self.assertTrue(App.start_manual_motor_mode(app))
        self.assertEqual(app.commands[0][0], "stop")
        self.assertTrue(app.auto.get())
        self.assertFalse(any(app.override[key].get() for key in ("first", "stars", "p1")))
        self.assertEqual(app.timeline_applied, [(12.0, True)])
        sent = app.sent[-1][1]
        self.assertEqual((sent["angle"], sent["speed"]), (42.0, 0.0))
        self.assertTrue(sent["first"] and sent["p1"])

    def test_relative_move_requires_armed_mode(self):
        app = FakeApp()
        app.manual_motor_mode = True
        with patch("app.messagebox.showwarning"):
            self.assertFalse(App.move_manual_motor(app, -15.0, 5.0))
        self.assertEqual(app.commands, [])
        app.manual_motor_armed = True
        self.assertTrue(App.move_manual_motor(app, -15.0, 5.0))
        self.assertEqual(app.commands, [("move_relative", 5.0, -15.0)])

    def test_return_to_timeline_clears_only_motor_overrides(self):
        app = FakeApp()
        app.manual_motor_mode = True
        app.override["angle"].set(True)
        app.override["speed"].set(True)
        app.override["first"].set(True)
        app.manual["first"].set("ON")
        with patch("app.messagebox.askyesno", return_value=True):
            self.assertTrue(App.leave_manual_motor_mode(app))
        self.assertEqual(app.commands[0][0], "exit")
        self.assertFalse(app.manual_motor_mode)
        self.assertFalse(app.override["angle"].get())
        self.assertFalse(app.override["speed"].get())
        self.assertTrue(app.override["first"].get())
        self.assertEqual(app.sent[-1][1]["angle"], 90.0)


if __name__ == "__main__":
    unittest.main()
