"""植物大战僵尸 — 入口文件。

初始化 Pygame，启动状态机，进入主循环。
"""

from __future__ import annotations

import sys

import pygame

from source.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, FPS
from source.state.state_machine import StateMachine
from source.state.menu_state import MenuState


def main() -> None:
    """应用程序入口。"""
    # ── 初始化 Pygame ─────────────────────────────
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # ── 初始化状态机 ──────────────────────────────
    state_machine = StateMachine()
    state_machine.push(MenuState(state_machine))

    # ── 主循环 ────────────────────────────────────
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # delta time（秒）

        # 事件分发
        for event in pygame.event.get():
            if state_machine.current is not None:
                state_machine.current.handle_event(event)

        # 逻辑更新
        if state_machine.current is not None:
            state_machine.current.update(dt)

        # 渲染
        if state_machine.current is not None:
            state_machine.current.draw(screen)
        else:
            # 状态栈已空 → 退出
            running = False

        pygame.display.flip()

        # 状态机被清空时退出
        if state_machine.is_empty:
            running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
