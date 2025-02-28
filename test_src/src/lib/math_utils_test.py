import math

from src.lib.math_utils import *

import unittest

class TestMathUtils(unittest.TestCase):
    def test_angle_between_vectors(self):
        self.assertEqual(angle_between((1, 0), (0, 1)), math.pi / 2)
        self.assertEqual(angle_between((0, 1), (1, 0)), math.pi / 2)

        self.assertEqual(angle_between((0, 1), (0, 1)), 0.0)
        self.assertEqual(angle_between((0, 1), (0, -1)), math.pi)

        self.assertEqual(signed_angle_between((1, 0), (0, 1)), -math.pi / 2)
        self.assertEqual(signed_angle_between((0, 1), (1, 0)), math.pi / 2)

    def test_more_angles_between_vectors(self):
        self.assertAlmostEqual(signed_angle_between((0.1, 1.0), (0.3, -0.3)), 2.2565, delta=0.0001)
        self.assertAlmostEqual(signed_angle_between((0.3, -0.3), (0.1, 1.0)), -2.2565, delta=0.0001)

if __name__ == '__main__':
    unittest.main()