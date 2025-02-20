import unittest

from src.lib.configuration import *


class TestConfiguration(unittest.TestCase):
    def test_get_conf(self):
        conf = Configuration("test_src/src/lib/example_conf.toml")

        self.assertEqual(conf.get_conf_str("test1", "name", fail=False), "John")
        self.assertEqual(conf.get_conf_num("test1", "time", fail=False), 123)
        self.assertEqual(conf.get_conf_num_f("test1", "money", fail=False), 16.2)

        self.assertEqual(conf.get_conf_str("test2", "name", fail=False), "Adam")
        self.assertEqual(conf.get_conf_num("test2", "time", fail=False), 999)
        self.assertEqual(conf.get_conf_num_f("test2", "money", fail=False), -16.2)

if __name__ == '__main__':
    unittest.main()