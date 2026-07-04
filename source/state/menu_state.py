"""主菜单状态。"""

from __future__ import annotations

import pygame

from source.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_BLACK
from source.state.state_machine import GameState, StateMachine


class MenuState(GameState):
    """主菜单 — 显示标题 + "开始游戏"按钮。"""

    def __init__(self, machine: StateMachine) -> None:
        super().__init__(machine)
        self._font_title: pygame.font.Font | None = None
        self._font_button: pygame.font.Font | None = None
        self._button_rect: pygame.Rect | None = None
        self._bg_color: tuple[int, int, int] = (30, 30, 60)

    def enter(self, *args, **kwargs) -> None:
        self._font_title = pygame.font.Font(None, 72)
        self._font_button = pygame.font.Font(None, 36)

        # 按钮位置（屏幕中央偏下）
        btn_w, btn_h = 220, 60
        self._button_rect = pygame.Rect(
            (SCREEN_WIDTH - btn_w) // 2,
            int(SCREEN_HEIGHT * 0.6),
            btn_w,
            btn_h,
        )

    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            # 清空状态机 → 主循环退出
            self.machine.clear()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._button_rect and self._button_rect.collidepoint(event.pos):
                # 延迟导入，避免循环依赖
                from source.state.level_state import LevelState  # noqa: PLC0415

                self.machine.push(LevelState(self.machine))

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(self._bg_color)

        # 标题
        if self._font_title:
            title_surf = self._font_title.render("植物大战僵尸", True, COLOR_WHITE)
            title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            screen.blit(title_surf, title_rect)

        # 按钮
        if self._button_rect and self._font_button:
            pygame.draw.rect(screen, (60, 60, 160), self._button_rect, border_radius=8)
            btn_text = self._font_button.render("开始游戏", True, COLOR_WHITE)
            btn_text_rect = btn_text.get_rect(center=self._button_rect.center)
            screen.blit(btn_text, btn_text_rect)
