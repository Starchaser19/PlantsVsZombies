"""子弹实体 — PeaBullet + SnowPeaBullet（真实精灵渲染）。"""

from __future__ import annotations

import pygame

from source.constants import SCREEN_WIDTH
from source.entity.game_object import GameObject
from source.utils.sprite_loader import load_frames


class Bullet(GameObject):
    """子弹基类。"""

    def __init__(
        self,
        x: float,
        y: float,
        row: int,
        damage: int = 20,
        speed: float = 350.0,
    ) -> None:
        super().__init__(x, y, 56, 34, hp=1)
        self.row = row
        self.damage = damage
        self.speed = speed
        self._image: pygame.Surface | None = None

    def update(self, dt: float, **kwargs) -> None:
        if not self.alive:
            return
        self.rect.x += self.speed * dt
        if self.rect.left > SCREEN_WIDTH:
            self.alive = False

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return
        if self._image is not None:
            screen.blit(self._image, self.rect)


class PeaBullet(Bullet):
    """豌豆子弹。"""

    _sprite: pygame.Surface | None = None

    def __init__(self, x: float, y: float, row: int, damage: int = 20) -> None:
        super().__init__(x=x, y=y, row=row, damage=damage)
        if PeaBullet._sprite is None:
            frames = load_frames("Bullets/PeaNormal", "PeaNormal")
            PeaBullet._sprite = frames[0] if frames else None
        self._image = PeaBullet._sprite


class SnowPeaBullet(Bullet):
    """冰冻豌豆 — 命中后减速僵尸。"""

    _sprite: pygame.Surface | None = None

    def __init__(
        self,
        x: float,
        y: float,
        row: int,
        damage: int = 20,
        slow_duration: float = 3.0,
    ) -> None:
        super().__init__(x=x, y=y, row=row, damage=damage)
        self.slow_duration = slow_duration
        if SnowPeaBullet._sprite is None:
            frames = load_frames("Bullets/PeaIce", "PeaIce")
            SnowPeaBullet._sprite = frames[0] if frames else None
        self._image = SnowPeaBullet._sprite

    def apply_slow(self, zombie) -> None:
        """对僵尸施加减速效果。"""
        zombie.apply_slow(self.slow_duration)
