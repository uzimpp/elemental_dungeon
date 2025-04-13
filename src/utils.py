# utils.py
import math
import pygame


def resolve_overlap(a, b):
    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.hypot(dx, dy)
    min_dist = a.radius + b.radius
    if dist == 0:
        dist = 0.1
    if dist < min_dist:
        overlap = min_dist - dist
        push_x = dx / dist * (overlap / 2.0)
        push_y = dy / dist * (overlap / 2.0)
        a.x -= push_x
        a.y -= push_y
        b.x += push_x
        b.y += push_y


def angle_diff(a, b):
    """
    Returns the absolute difference between two angles a and b,
    normalized to the range [0, pi].
    """
    diff = (b - a) % (2 * math.pi)
    if diff > math.pi:
        diff = 2 * math.pi - diff
    return abs(diff)


def draw_hp_bar(
        surface,
        x,
        y,
        current_hp,
        max_hp,
        bar_color,
        bar_width=50,
        bar_height=6):
    """
    Draw a simple HP bar at (x, y) with the given color and size.
    Bar fill depends on current_hp / max_hp.
    """
    if current_hp < 0:
        current_hp = 0
    pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_width, bar_height))
    hp_frac = current_hp / max_hp if max_hp > 0 else 0
    if hp_frac < 0:
        hp_frac = 0
    fill_width = int(bar_width * hp_frac)
    pygame.draw.rect(surface, bar_color, (x, y, fill_width, bar_height))
