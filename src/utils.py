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
    dist_sq = dx*dx + dy*dy

    # Combined radius
    min_dist = a.radius + b.radius

    if dist_sq >= min_dist * min_dist and dist_sq != 0:
        return

    if dist_sq == 0:
        move_offset = a.radius * 0.1 if a.radius > 0 else 0.1
        a.x -= move_offset
        dx = b.x - a.x
        dy = b.y - a.y
        dist_sq = dx*dx + dy*dy
        if dist_sq == 0:
            return  # Cannot resolve further

    dist = math.sqrt(dist_sq)  # Calculate actual distance

    if dist < min_dist:
        overlap = min_dist - dist

        if dist == 0:

            return
        nx = dx / dist
        ny = dy / dist
        # Amount to move each object along the separation axis
        move_amount = overlap / 2.0
        a.x -= nx * move_amount
        a.y -= ny * move_amount
        b.x += nx * move_amount
        b.y += ny * move_amount


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
