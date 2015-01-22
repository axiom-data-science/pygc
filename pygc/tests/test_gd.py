import unittest
import numpy as np
from pygc import great_distance


class GreatDistanceTest(unittest.TestCase):

    def test_great_distance_scalars(self):
        # One decimal degree at the equator is about 111.32km
        latitude_start  = 0.
        latitude_end    = 0.
        longitude_start = 50.
        longitude_end   = 52.

        gd = great_distance(start_latitude=latitude_start, start_longitude=longitude_start, end_latitude=latitude_end, end_longitude=longitude_end)
        assert round(gd['distance'] / 1000, 2) == 111.32 * 2

    def test_great_distance_numpy(self):
        # One decimal degree is 111000m
        latitude_start  = 0.
        latitude_end    = 0.
        longitude_start = [49., 75.]
        longitude_end   = [50., 76.]

        gd = great_distance(start_latitude=latitude_start, start_longitude=longitude_start, end_latitude=latitude_end, end_longitude=longitude_end)
        assert np.allclose(gd["distance"] / 1000, 111.32)
