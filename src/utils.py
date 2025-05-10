"""
Utility functions for the Incantato game.
Contains math helpers and other common utility functions.
"""
import math

class Utils:
    """
    Static utility class providing helper functions for game calculations.
    """
    @staticmethod
    def angle_diff(a, b):
        """
        Returns the absolute difference between two angles a and b,
        normalized to the range [0, pi].
        
        Args:
            a (float): First angle in radians
            b (float): Second angle in radians
            
        Returns:
            float: The absolute angular difference in radians
        """
        diff = (b - a) % (2 * math.pi)
        if diff > math.pi:
            diff = 2 * math.pi - diff
        return abs(diff)
