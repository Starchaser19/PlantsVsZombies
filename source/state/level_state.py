"""核心游戏关卡状态。"""

from __future__ import annotations

import pygame

from source.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_WHITE,
    COLOR_BLACK,
    COLOR_GRAY,
    COLOR_GREEN,
)
from source.map.grid_map import GridMap
from source.state.state_machine import GameState, StateMachine


class LevelState(GameState):
    """游戏内状态 — 植物大战僵尸的核心循环。"""

    def __init__(self, machine: StateMachine) -> None:
        super().__init__(machine)
        self._grid_map = GridMap()
        self._font: pygame.font.Font | None = None
        self._font_small: pygame.font.Font | None = None
        # 调试：记录最近一次点击的网格坐标
        self._last_click: tuple[int, int] | None = None

    def enter(self, *args, **kwargs) -> None:
        self._font = pygame.font.Font(None, 32)
        self._font_small = pygame.font.Font(None, 20)

    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.machine.clear()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # 返回主菜单
                self.machine.pop()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 鼠标点击 → 转换网格坐标并记录
            grid_pos = GridMap.screen_to_grid(*event.pos)
            self._last_click = grid_pos
            if grid_pos:
                print(f"[LevelState] 点击网格: col={grid_pos[0]}, row={grid_pos[1]}")

    def update(self, dt: float) -> None:
        # Phase 2 将在此加入游戏逻辑
        pass

    def draw(self, screen: pygame.Surface) -> None:
        # 背景
        screen.fill((100, 149, 237))  # 天空蓝

        # 草坪网格
        self._grid_map.draw(screen)

        # 顶部信息栏占位
        top_bar = pygame.Rect(0, 0, SCREEN_WIDTH, MAP_OFFSET_Y - 10)
        pygame.draw.rect(screen, (50, 40, 30), top_bar)

        if self._font:
            sun_text = self._font.render("☀ 150", True, COLOR_WHITE)
            screen.blit(sun_text, (20, 25))

        # 底部提示
        if self._font_small:
            hint = self._font_small.render(
                "ESC: 返回菜单 | 点击草坪放置植物 (开发中)",
                True,
                COLOR_WHITE,
            )
            screen.blit(hint, (20, SCREEN_HEIGHT - 30))

        # 调试：高亮上次点击的格子
        if self._last_click and self._font_small:
            col, row = self._last_click
            x, y = GridMap.grid_to_screen(col, row)
            rect = pygame.Rect(x, y, GRID_X_SIZE, GRID_Y_SIZE)
            pygame.draw.rect(screen, (255, 255, 0), rect, width=3)
            coord_text = self._font_small.render(
                f"({col}, {row})", True, COLOR_WHITE
            )
            screen.blit(coord_text, (x + 5, y + 5))


# 本地引用常量，避免冗长前缀
from source.constants import MAP_OFFSET_Y, GRID_X_SIZE, GRID_Y_SIZE  # noqa: E402
