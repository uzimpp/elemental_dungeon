# utils.py
import math
import pygame

class Utils:
    @staticmethod
    def angle_diff(a, b):
        """
        Returns the absolute difference between two angles a and b,
        normalized to the range [0, pi].
        """
        diff = (b - a) % (2 * math.pi)
        if diff > math.pi:
            diff = 2 * math.pi - diff
        return abs(diff)
