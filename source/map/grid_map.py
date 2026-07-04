"""9x5 网格地图 — 坐标转换 + 渲染 + 点击检测。"""

from __future__ import annotations

from typing import Optional

import pygame

from source.constants import (
    GRID_COLS,
    GRID_ROWS,
    GRID_X_SIZE,
    GRID_Y_SIZE,
    MAP_OFFSET_X,
    MAP_OFFSET_Y,
    COLOR_GREEN,
    COLOR_LIGHT_GREEN,
    COLOR_BROWN,
)


class GridMap:
    """草坪网格地图。

    网格坐标系: (map_x, map_y)，其中 map_x ∈ [0, GRID_COLS), map_y ∈ [0, GRID_ROWS).
    屏幕坐标系: (screen_x, screen_y)，pygame 原生像素坐标。
    """

    # ── 坐标转换（静态方法，纯函数，方便测试） ──────────

    @staticmethod
    def screen_to_grid(screen_x: int, screen_y: int) -> Optional[tuple[int, int]]:
        """屏幕坐标 → 网格坐标。返回 None 表示不在网格范围内。"""
        map_x = (screen_x - MAP_OFFSET_X) // GRID_X_SIZE
        map_y = (screen_y - MAP_OFFSET_Y) // GRID_Y_SIZE
        if 0 <= map_x < GRID_COLS and 0 <= map_y < GRID_ROWS:
            return map_x, map_y
        return None

    @staticmethod
    def grid_to_screen(map_x: int, map_y: int) -> tuple[int, int]:
        """网格坐标 → 屏幕左上角像素坐标。"""
        screen_x = map_x * GRID_X_SIZE + MAP_OFFSET_X
        screen_y = map_y * GRID_Y_SIZE + MAP_OFFSET_Y
        return screen_x, screen_y

    @staticmethod
    def grid_center(map_x: int, map_y: int) -> tuple[int, int]:
        """网格坐标 → 格子中心像素坐标。"""
        left, top = GridMap.grid_to_screen(map_x, map_y)
        return left + GRID_X_SIZE // 2, top + GRID_Y_SIZE // 2

    # ── 实例方法 ───────────────────────────────────────

    def draw(self, screen: pygame.Surface) -> None:
        """绘制草坪网格（开发阶段占位渲染）。"""
        # 背景底色
        grid_rect = pygame.Rect(
            MAP_OFFSET_X,
            MAP_OFFSET_Y,
            GRID_COLS * GRID_X_SIZE,
            GRID_ROWS * GRID_Y_SIZE,
        )
        pygame.draw.rect(screen, COLOR_GREEN, grid_rect)

        # 每个格子
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x, y = self.grid_to_screen(col, row)
                cell_rect = pygame.Rect(x, y, GRID_X_SIZE, GRID_Y_SIZE)
                # 交替颜色
                color = COLOR_LIGHT_GREEN if (row + col) % 2 == 0 else COLOR_GREEN
                pygame.draw.rect(screen, color, cell_rect)
                pygame.draw.rect(screen, COLOR_BROWN, cell_rect, width=1)

    def is_valid_cell(self, map_x: int, map_y: int) -> bool:
        """检查网格坐标是否在有效范围内。"""
        return 0 <= map_x < GRID_COLS and 0 <= map_y < GRID_ROWS
