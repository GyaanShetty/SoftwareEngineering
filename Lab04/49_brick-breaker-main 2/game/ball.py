import math
import pygame


class Ball:
    def __init__(self, x, y, radius=8):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.vx = 0.0
        self.vy = 0.0

    @property
    def speed(self):
        return math.hypot(self.vx, self.vy)

    def move(self, fraction=1.0):
        """Advance by a fraction of one frame's velocity (used for sub-stepping)."""
        self.x += self.vx * fraction
        self.y += self.vy * fraction

    def bounds(self):
        """Float AABB: (left, top, right, bottom)."""
        r = self.radius
        return self.x - r, self.y - r, self.x + r, self.y + r

    def rect(self):
        return pygame.Rect(round(self.x - self.radius), round(self.y - self.radius),
                           self.radius * 2, self.radius * 2)
