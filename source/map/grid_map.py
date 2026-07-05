"""9×5 草坪网格 — 坐标转换。背景图已含草坪纹理，不额外绘制格子。"""

from __future__ import annotations

from typing import Optional

from source.constants import (
    GRID_COLS, GRID_ROWS, GRID_X_SIZE, GRID_Y_SIZE,
    MAP_OFFSET_X, MAP_OFFSET_Y,
)


class GridMap:
    """草坪网格，仅负责坐标转换。"""

    @staticmethod
    def screen_to_grid(screen_x: int, screen_y: int) -> Optional[tuple[int, int]]:
        map_x = (screen_x - MAP_OFFSET_X) // GRID_X_SIZE
        map_y = (screen_y - MAP_OFFSET_Y) // GRID_Y_SIZE
        if 0 <= map_x < GRID_COLS and 0 <= map_y < GRID_ROWS:
            return map_x, map_y
        return None

    @staticmethod
    def grid_to_screen(map_x: int, map_y: int) -> tuple[int, int]:
        return (
            map_x * GRID_X_SIZE + MAP_OFFSET_X,
            map_y * GRID_Y_SIZE + MAP_OFFSET_Y,
        )

    @staticmethod
    def grid_center(map_x: int, map_y: int) -> tuple[int, int]:
        left, top = GridMap.grid_to_screen(map_x, map_y)
        return left + GRID_X_SIZE // 2, top + GRID_Y_SIZE // 2

    def is_valid_cell(self, map_x: int, map_y: int) -> bool:
        return 0 <= map_x < GRID_COLS and 0 <= map_y < GRID_ROWS

    def draw(self, screen) -> None:
        """背景图已有草坪纹理，无需额外绘制。"""
        pass
