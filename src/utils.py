# utils.py
import math
import pygame


def resolve_overlap(a, b):
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
