"""
Utility functions for the Incantato game.

Provides helper functions for collision resolution and angle calculations.
"""
import math


def resolve_overlap(a, b):
    """
    Resolve collision overlap between two circular objects.

    Moves both objects apart to prevent overlapping based on their
    positions and radii.

    Args:
        a: First object with x, y, and radius properties
        b: Second object with x, y, and radius properties
    """
    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.hypot(dx, dy)
    min_dist = a.radius + b.radius
    if dist == 0:
        dist = 0.00000001
    if dist < min_dist:
        overlap = min_dist - dist
        push_x = dx / dist * (overlap / 2.0)
        push_y = dy / dist * (overlap / 2.0)
        a.x -= push_x
        a.y -= push_y
        b.x += push_x
        b.y += push_y


class Utils:
    """Utility class with static helper methods."""

    @staticmethod
    def angle_diff(a, b):
        """
        Returns the absolute difference between two angles a and b,
        normalized to the range [0, pi].

        Args:
            a: First angle in degrees
            b: Second angle in degrees

        Returns:
            float: The smallest angular difference between the angles
        """
        diff = abs(a - b) % 360
        return min(diff, 360 - diff)
