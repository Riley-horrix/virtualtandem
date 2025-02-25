import unittest

from src.lib.configuration import Configuration
from src.lib.geofence import Geofence

class TestGeofence(unittest.TestCase):
    def test_geofence_basic(self):
        geo = Geofence()
        geo.initialise(Configuration("test_src/src/lib/geofence1.toml"))

        # Points inside the unit square geofence (0,0) to (1,1)
        self.assertTrue(geo.inside_geofence(0.5, 0.5))
        self.assertTrue(geo.inside_geofence(0.1, 0.9))
        self.assertTrue(geo.inside_geofence(0.0, 0.0))

        # Points outside the unit square geofence
        self.assertFalse(geo.inside_geofence(-0.1, 0.5))
        self.assertFalse(geo.inside_geofence(1.1, 0.5))
        self.assertFalse(geo.inside_geofence(0.5, 1.1))
        self.assertFalse(geo.inside_geofence(1.5, 1.5))

        # Edge cases
        self.assertTrue(geo.inside_geofence(0.0, 0.0))
        self.assertTrue(geo.inside_geofence(1.0, 1.0))
        self.assertTrue(geo.inside_geofence(1.0, 0.5))
        self.assertTrue(geo.inside_geofence(0.5, 1.0))

    def test_geofence_distance_basic(self):
        geo = Geofence()
        geo.initialise(Configuration("test_src/src/lib/geofence1.toml"))

        self.assertAlmostEqual(geo.distance_to_closest_wall(0.5, 0.5, 0)[0], 0.5)
        self.assertAlmostEqual(geo.distance_to_closest_wall(0.5, 0.5, 1.5708)[0], 0.5)
        self.assertAlmostEqual(geo.distance_to_closest_wall(0.5, 0.5, 3.1416)[0], 0.5)
        self.assertAlmostEqual(geo.distance_to_closest_wall(0.5, 0.5, 4.7124)[0], 0.5)

        self.assertAlmostEqual(geo.distance_to_closest_wall(0.1, 0.9, 0)[0], 0.1)
        self.assertAlmostEqual(geo.distance_to_closest_wall(0.9, 0.1, 3.1416)[0], 0.1)

        self.assertAlmostEqual(geo.distance_to_closest_wall(0.7, 0.6, 2.35619)[0], 0.4242, delta=0.0001)
        self.assertAlmostEqual(geo.distance_to_closest_wall(0.8, 0.9, 3.92699)[0], 1.1313, delta=0.0001)


if __name__ == '__main__':
    unittest.main()