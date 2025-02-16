import unittest
from src.math_ops import MathOps


class TestMathOps(unittest.TestCase):
    def test_add(self):
        math_obj = MathOps()
        self.assertEqual(math_obj.add(2, 3), 5)

    def test_multiply(self):
        math_obj = MathOps()
        self.assertEqual(math_obj.multiply(2, 3), 6)


if __name__ == "__main__":
    unittest.main()
