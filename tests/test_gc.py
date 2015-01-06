import unittest
import numpy as np
from pygc import great_circle


class GreatCircleTest(unittest.TestCase):

    def test_great_circle_scalars(self):
        # One decimal degree is 111000m
        latitude  = 40.0
        longitude = -76.0

        azimuth = 90
        new_gc = great_circle(distance=111000, azimuth=azimuth, latitude=latitude, longitude=longitude)
        # We should have gone to the right
        assert new_gc["longitude"] > longitude + 0.9

        azimuth = 270
        new_gc = great_circle(distance=111000, azimuth=azimuth, latitude=latitude, longitude=longitude)
        # We should have gone to the left
        assert new_gc["longitude"] < longitude - 0.9

        azimuth = 180
        new_gc = great_circle(distance=111000, azimuth=azimuth, latitude=latitude, longitude=longitude)
        # We should have gone down
        assert new_gc["latitude"] < latitude - 0.9

        azimuth = 0
        new_gc = great_circle(distance=111000, azimuth=azimuth, latitude=latitude, longitude=longitude)
        # We should have gone up
        assert new_gc["latitude"] > latitude + 0.9

        azimuth = 315
        new_gc = great_circle(distance=111000, azimuth=azimuth, latitude=latitude, longitude=longitude)
        # We should have gone up and to the left
        assert new_gc["latitude"] > latitude + 0.45
        assert new_gc["longitude"] < longitude - 0.45

    def test_great_circle_numpy(self):
        # One decimal degree is 111000m
        latitude  = np.asarray([40.0, 50.0, 60.0])
        longitude = np.asarray([-76.0, -86.0, -96.0])

        azimuth = 90
        new_gc = great_circle(distance=111000, azimuth=azimuth, latitude=latitude, longitude=longitude)
        # We should have gone to the right
        assert (new_gc["longitude"] > longitude + 0.9).all()

        azimuth = 270
        new_gc = great_circle(distance=111000, azimuth=azimuth, latitude=latitude, longitude=longitude)
        # We should have gone to the left
        assert (new_gc["longitude"] < longitude - 0.9).all()

        azimuth = 180
        new_gc = great_circle(distance=111000, azimuth=azimuth, latitude=latitude, longitude=longitude)
        # We should have gone down
        assert (new_gc["latitude"] < latitude - 0.9).all()

        azimuth = 0
        new_gc = great_circle(distance=111000, azimuth=azimuth, latitude=latitude, longitude=longitude)
        # We should have gone up
        assert (new_gc["latitude"] > latitude + 0.9).all()

        azimuth = 315
        new_gc = great_circle(distance=111000, azimuth=azimuth, latitude=latitude, longitude=longitude)
        # We should have gone up and to the left
        assert (new_gc["latitude"] > latitude + 0.45).all()
        assert (new_gc["longitude"] < longitude - 0.45).all()
