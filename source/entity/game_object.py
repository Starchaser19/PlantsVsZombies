"""GameObject 基类 — 所有游戏实体的抽象父类。"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pygame


class GameObject(ABC):
    """游戏对象基类。

    Attributes:
        rect: 碰撞矩形（也是渲染位置）。
        hp: 当前生命值。
        max_hp: 最大生命值。
        alive: 是否存活。死亡后由 EntityManager 清理。
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: int,
        height: int,
        hp: int = 100,
    ) -> None:
        self.rect = pygame.Rect(int(x), int(y), width, height)
        self.hp = hp
        self.max_hp = hp
        self.alive = True

    # ── 接口 ──────────────────────────────────────────

    @abstractmethod
    def update(self, dt: float, **kwargs) -> None:
        """每帧逻辑更新。子类必须实现。"""

    def draw(self, screen: pygame.Surface) -> None:
        """默认渲染：绘制占位色块 + HP 文字。

        子类可重写以使用精灵帧。
        """
        if not self.alive:
            return
        color = self._get_color()
        pygame.draw.rect(screen, color, self.rect, border_radius=4)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, width=2)

    # ── 公共方法 ──────────────────────────────────────

    def take_damage(self, amount: int) -> None:
        """受到伤害。HP 归零时自动标记死亡。"""
        if not self.alive:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self._on_death()

    def _on_death(self) -> None:
        """死亡回调。子类可重写以播放动画/特效。"""

    def _get_color(self) -> tuple[int, int, int]:
        """返回占位渲染颜色。子类应重写。"""
        return (128, 128, 128)

    # ── 属性 ──────────────────────────────────────────

    @property
    def is_dead(self) -> bool:
        return not self.alive

    @property
    def hp_ratio(self) -> float:
        """HP 比例 [0, 1]，用于 HP 条渲染。"""
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0
