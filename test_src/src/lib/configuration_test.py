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

    def test_get_conf_list(self):
        conf = Configuration("test_src/src/lib/example_conf.toml")

        self.assertListEqual(conf.get_conf_list_f("listTest", "times"), [1.0, 2.4, 7.1])
        self.assertListEqual(conf.get_conf_list("listTest", "times_floor"), [1, 2, 7])

        self.assertListEqual(conf.get_conf_list_str("listTest", "string_list"), ["hello", "hi", "goodbye"])

        with self.assertRaises(ConfigurationException):
            conf.get_conf_list("listTest", "times")

        with self.assertRaises(ConfigurationException):
            conf.get_conf_list("listTest", "string_list")

    def test_get_conf_fail(self):
        conf = Configuration("test_src/src/lib/example_conf.toml")

        with self.assertRaises(ConfigurationException):
            conf.get_conf_str("test3", "str")

        with self.assertRaises(ConfigurationException):
            conf.get_conf_num("test3", "num")

        with self.assertRaises(ConfigurationException):
            conf.get_conf_num("test3", " numf")

        with self.assertRaises(ConfigurationException):
            conf.get_conf_list("test3", "list")

        with self.assertRaises(ConfigurationException):
            conf.get_conf_list_f("test3", "list f")

    def test_get_conf_bad_type(self):
        conf = Configuration("test_src/src/lib/example_conf.toml")
        with self.assertRaises(ConfigurationException):
            conf.get_conf_str("test1", "time")

        with self.assertRaises(ConfigurationException):
            conf.get_conf_num("test1", "name")



if __name__ == '__main__':
    unittest.main()