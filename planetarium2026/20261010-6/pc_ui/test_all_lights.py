import unittest

from app import App


class Variable:
    def __init__(self, value=False):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeApp:
    def __init__(self):
        keys = ["first", "stars"] + [f"p{i}" for i in range(1, 9)]
        self.emergency_stop = False
        self.override = {key: Variable(False) for key in keys}
        self.manual = {key: Variable("OFF") for key in keys}
        self.desired = {key: False for key in keys}
        self.messages = []
        self.sent = []

    def log(self, message):
        self.messages.append(message)

    def send(self, force=False):
        self.sent.append(force)

    def all_lights_are_on(self):
        return App.all_lights_are_on(self)

    def update_all_lights_button(self):
        pass


class AllLightsTests(unittest.TestCase):
    def test_button_toggles_all_channels_on_then_off(self):
        app = FakeApp()
        App.toggle_all_lights(app)
        self.assertTrue(all(value.get() for value in app.override.values()))
        self.assertTrue(all(value.get() == "ON" for value in app.manual.values()))
        App.toggle_all_lights(app)
        self.assertTrue(all(value.get() for value in app.override.values()))
        self.assertTrue(all(value.get() == "OFF" for value in app.manual.values()))
        self.assertEqual(app.sent, [True, True])
        self.assertEqual(len(app.messages), 2)

    def test_light_override_switch_preserves_manual_values(self):
        app = FakeApp()
        app.desired["first"] = True
        app.override["angle"] = Variable(True)
        app.manual["p1"].set("ON")
        App.toggle_light_overrides(app)
        self.assertTrue(all(app.override[key].get() for key in app.desired))
        App.toggle_light_overrides(app)
        self.assertTrue(all(not app.override[key].get() for key in app.desired))
        self.assertTrue(app.override["angle"].get())
        self.assertEqual(app.manual["p1"].get(), "ON")
        self.assertEqual(app.sent, [True, True])


if __name__ == "__main__":
    unittest.main()
