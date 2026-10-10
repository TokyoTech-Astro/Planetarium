import ast
import pathlib
import unittest


APP = pathlib.Path(__file__).with_name("app.py")


def load_function(name):
    tree = ast.parse(APP.read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    module = ast.Module(body=[node], type_ignores=[])
    namespace = {}
    exec(compile(module, str(APP), "exec"), namespace)
    return namespace[name]


zero_return_delta = load_function("zero_return_delta")


class ZeroReturnDeltaTests(unittest.TestCase):
    def test_clockwise(self):
        self.assertAlmostEqual(zero_return_delta(90, True), 270)

    def test_counterclockwise(self):
        self.assertAlmostEqual(zero_return_delta(90, False), -90)

    def test_wrapped_angle(self):
        self.assertAlmostEqual(zero_return_delta(450, True), 270)

    def test_already_zero(self):
        self.assertEqual(zero_return_delta(0, True), 0)
        self.assertEqual(zero_return_delta(359.995, False), 0)


if __name__ == "__main__":
    unittest.main()
