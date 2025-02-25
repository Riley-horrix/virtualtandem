import unittest
from colour_runner import runner

# Import all modules
# src
from test_src.src import task_handler_test, message_test, mcEstimator_test

# lib
from test_src.src.lib import configuration_test, geofence_test

def test_run():
    suite = unittest.TestSuite()

    def load_mod(mod) -> unittest.TestSuite:
        return unittest.defaultTestLoader.loadTestsFromModule(mod)

    suite.addTests([
        # src
        load_mod(task_handler_test),
        load_mod(message_test),
        load_mod(mcEstimator_test),

        # lib
        load_mod(configuration_test),
        load_mod(geofence_test),
    ])

    # unittest.TextTestRunner(verbosity=3).run(suite)
    runner.ColourTextTestRunner(verbosity=3).run(suite)

if __name__ == '__main__':
    test_run()