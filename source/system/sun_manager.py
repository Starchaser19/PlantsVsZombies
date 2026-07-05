"""阳光管理器 — 自然掉落 + 收集。"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from source.constants import SCREEN_WIDTH
from source.entity.sun import Sun

if TYPE_CHECKING:
    from source.entity.plant import Plant


class SunManager:
    """管理阳光的自然生成、收集和经济。"""

    NATURAL_INTERVAL = 8.0  # 自然阳光掉落间隔（秒）
    INITIAL_SUN = 300

    def __init__(self) -> None:
        self.sun_value = self.INITIAL_SUN
        self._natural_timer = self.NATURAL_INTERVAL

    def update(self, dt: float) -> list[Sun]:
        """更新自然阳光掉落。

        Returns:
            本次生成的新阳光列表（通常为空或 1 个）。
        """
        new_suns: list[Sun] = []

        self._natural_timer -= dt
        if self._natural_timer <= 0:
            self._natural_timer += self.NATURAL_INTERVAL
            # 在屏幕上方随机位置生成
            sun = Sun(
                x=random.randint(150, SCREEN_WIDTH - 150),
                y=-50,
                value=25,
                falling=True,
            )
            new_suns.append(sun)

        return new_suns

    def can_afford(self, cost: int) -> bool:
        """是否有足够阳光。"""
        return self.sun_value >= cost

    def spend(self, amount: int) -> None:
        """花费阳光。"""
        self.sun_value -= amount

    def add(self, amount: int) -> None:
        """增加阳光。"""
        self.sun_value += amount
