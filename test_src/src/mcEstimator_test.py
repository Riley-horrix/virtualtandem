import unittest

from src.mc_estimator import *
from src.message import MessageHub
from src.task_handler import TaskHandler
from src.lib.configuration import Configuration


class TestMcEstimator(unittest.TestCase):
    def test_can_produce_accurate_estimate(self):
        task_handler = TaskHandler()

        hub = MessageHub(task_handler)
        estimator = MonteCarloPositionEstimator(hub)

        # Defines vehicle starting at 0, 0
        estimator.initialise(Configuration("test_src/src/mcEstimator_test1.toml"))

        # Should move to 8.660254038, 5
        distance_theta = 0.0
        theta_std = 0.0

        for _ in range(3):
            estimator.send(MoveEstimate(10.0 / 3.0, distance_theta, theta_std))

        self.assertAlmostEqual(estimator.estimate_position()[0], 5.0, delta=0.01)
        self.assertAlmostEqual(estimator.estimate_position()[1], 8.66, delta=0.01)
        self.assertAlmostEqual(estimator.estimate_position()[2], 0.52, delta=0.01)

        estimator.initialise(Configuration("test_src/src/mcEstimator_test2.toml"))

        # Should move to 8.660254038, 5
        distance_theta = 0.0
        theta_std = 0.0

        for _ in range(3):
            estimator.send(MoveEstimate(10.0 / 3.0, distance_theta, theta_std))

        self.assertAlmostEqual(estimator.estimate_position()[0], -3.0, delta=0.01)
        self.assertAlmostEqual(estimator.estimate_position()[1], 9.66, delta=0.01)
        self.assertAlmostEqual(estimator.estimate_position()[2], math.pi * 2 - 0.523, delta=0.001)


if __name__ == '__main__':
    unittest.main()