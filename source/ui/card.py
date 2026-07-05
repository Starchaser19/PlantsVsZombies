"""植物卡片 — 工具栏中的可选择卡片（真实精灵渲染）。"""

from __future__ import annotations

import pygame

from source.constants import COLOR_WHITE
from source.utils.sprite_loader import load_image


class Card:
    """一张植物卡片。"""

    WIDTH = 65
    HEIGHT = 90

    def __init__(
        self,
        plant_type: str,
        sun_cost: int,
        cooldown: float,
        label: str,
    ) -> None:
        self.plant_type = plant_type
        self.sun_cost = sun_cost
        self.cooldown = cooldown
        self.label = label
        self.rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)
        self._cooldown_remaining = 0.0
        self._font = pygame.font.Font(None, 16)

        # 加载卡片图片
        card_path = f"Cards/card_{plant_type}.png"
        try:
            self._image = load_image(card_path)
            # 缩放以适配卡片尺寸
            self._image = pygame.transform.scale(self._image, (self.WIDTH, self.HEIGHT))
        except FileNotFoundError:
            self._image = None

    def set_position(self, x: int, y: int) -> None:
        self.rect.topleft = (x, y)

    def start_cooldown(self) -> None:
        self._cooldown_remaining = self.cooldown

    def update(self, dt: float) -> None:
        if self._cooldown_remaining > 0:
            self._cooldown_remaining -= dt
            if self._cooldown_remaining < 0:
                self._cooldown_remaining = 0.0

    @property
    def is_ready(self) -> bool:
        return self._cooldown_remaining <= 0

    @property
    def cooldown_ratio(self) -> float:
        if self.cooldown <= 0:
            return 0.0
        return self._cooldown_remaining / self.cooldown

    def draw(self, screen: pygame.Surface, can_afford: bool = True) -> None:
        # 卡片底图
        if self._image is not None:
            if not can_afford or not self.is_ready:
                # 不可用时半透明
                img = self._image.copy()
                img.set_alpha(128)
                screen.blit(img, self.rect)
            else:
                screen.blit(self._image, self.rect)
        else:
            # 回退：纯色方块
            color = (100, 100, 100)
            pygame.draw.rect(screen, color, self.rect, border_radius=4)

        # 边框
        border_color = (255, 255, 255) if (can_afford and self.is_ready) else (128, 128, 128)
        pygame.draw.rect(screen, border_color, self.rect, width=2, border_radius=4)

        # 冷却遮罩
        if not self.is_ready:
            mask_h = int(self.HEIGHT * self.cooldown_ratio)
            if mask_h > 0:
                mask = pygame.Surface((self.WIDTH, mask_h), pygame.SRCALPHA)
                mask.fill((0, 0, 0, 120))
                screen.blit(mask, (self.rect.x, self.rect.y))

        # 阳光费用（左下角）
        cost_surf = self._font.render(f"☀{self.sun_cost}", True, (255, 255, 255))
        screen.blit(cost_surf, (self.rect.x + 4, self.rect.bottom - 16))
