"""割草机 — 参照原版红色手推式造型。"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from source.constants import MAP_OFFSET_X, MAP_OFFSET_Y, GRID_Y_SIZE, SCREEN_WIDTH
from source.entity.game_object import GameObject

if TYPE_CHECKING:
    from source.entity.zombie import Zombie


class LawnMower(GameObject):
    """割草机。"""

    SPEED = 400.0
    WIDTH = 68
    HEIGHT = 44

    def __init__(self, row: int) -> None:
        x = MAP_OFFSET_X - self.WIDTH + 10
        y = MAP_OFFSET_Y + row * GRID_Y_SIZE + (GRID_Y_SIZE - self.HEIGHT) // 2
        super().__init__(x, y, self.WIDTH, self.HEIGHT, hp=1)
        self._fx = float(x)
        self.row = row
        self.triggered = False

    def update(self, dt: float, **kwargs) -> None:
        if not self.alive or not self.triggered:
            return
        self._fx += self.SPEED * dt
        self.rect.x = int(self._fx)
        if self.rect.left > SCREEN_WIDTH:
            self.alive = False
        zombies: list[Zombie] = kwargs.get("zombies", [])
        for z in zombies:
            if z.alive and z.row == self.row and self.rect.colliderect(z.rect):
                z.take_damage(1800)

    def check_trigger(self, zombies: list[Zombie]) -> bool:
        if self.triggered or not self.alive:
            return False
        for z in zombies:
            if z.alive and z.row == self.row and z.rect.left <= MAP_OFFSET_X - 10:
                self.triggered = True
                return True
        return False

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return
        r = self.rect
        # 车身（红色）
        body_color = (220, 50, 30) if not self.triggered else (255, 80, 60)
        body = pygame.Rect(r.x + 8, r.y + 8, r.w - 16, r.h - 14)
        pygame.draw.rect(screen, body_color, body, border_radius=4)
        # 深色边框
        pygame.draw.rect(screen, (140, 20, 10), body, width=2, border_radius=4)
        # 集草袋（后方深色方块）
        bag = pygame.Rect(r.x + 2, r.y + 14, 10, r.h - 24)
        pygame.draw.rect(screen, (60, 50, 40), bag, border_radius=2)
        # 把手（金属杆）
        handle_x = r.right - 6
        pygame.draw.line(screen, (160, 160, 160),
                         (handle_x, r.y + 6), (handle_x + 8, r.y - 6), 3)
        pygame.draw.line(screen, (160, 160, 160),
                         (handle_x, r.y + 6), (handle_x + 14, r.y - 2), 2)
        # 轮子
        wr = 7
        pygame.draw.circle(screen, (30, 30, 30),
                           (r.left + 16, r.bottom - wr), wr)
        pygame.draw.circle(screen, (30, 30, 30),
                           (r.right - 16, r.bottom - wr), wr)
        # 轮轴
        pygame.draw.circle(screen, (80, 80, 80),
                           (r.left + 16, r.bottom - wr), 3)
        pygame.draw.circle(screen, (80, 80, 80),
                           (r.right - 16, r.bottom - wr), 3)
