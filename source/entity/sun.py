"""阳光实体 — 掉落、收集（真实精灵渲染）。"""

from __future__ import annotations

import random

import pygame

from source.constants import SCREEN_HEIGHT
from source.entity.game_object import GameObject
from source.utils.animation import Animation
from source.utils.sprite_loader import load_frames


class Sun(GameObject):
    """阳光实体。"""

    FALL_SPEED = 80.0
    LIFETIME = 10.0
    COLLECT_RADIUS = 40

    _frames: list[pygame.Surface] | None = None

    def __init__(
        self,
        x: float,
        y: float,
        value: int = 25,
        *,
        falling: bool = True,
        target_y: float | None = None,
    ) -> None:
        super().__init__(x, y, 78, 78, hp=1)
        self.value = value
        self.falling = falling
        self.collected = False
        self._lifetime = self.LIFETIME

        if Sun._frames is None:
            Sun._frames = load_frames("Plants/Sun", "Sun")
        self._anim = Animation(Sun._frames, frame_duration=0.1)

        if falling and target_y is None:
            target_y = random.randint(150, SCREEN_HEIGHT - 200)
        self._target_y = target_y or y

    def update(self, dt: float, **kwargs) -> None:
        if not self.alive or self.collected:
            return

        self._anim.update(dt)

        if self.falling:
            self.rect.y += self.FALL_SPEED * dt
            if self.rect.y >= self._target_y:
                self.rect.y = self._target_y
                self.falling = False

        self._lifetime -= dt
        if self._lifetime <= 0:
            self.alive = False

    def collect(self) -> int:
        self.collected = True
        self.alive = False
        return self.value

    def hit_test(self, pos: tuple[int, int]) -> bool:
        dx = pos[0] - self.rect.centerx
        dy = pos[1] - self.rect.centery
        return (dx * dx + dy * dy) <= self.COLLECT_RADIUS ** 2

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive or self.collected:
            return
        # 闪烁（快消失时）
        if self._lifetime < 3.0 and int(self._lifetime * 6) % 2 == 0:
            return
        img = self._anim.current_frame
        img_rect = img.get_rect(center=self.rect.center)
        screen.blit(img, img_rect)
