"""主菜单 — 官方背景 + 无尽模式入口。"""

from __future__ import annotations

import pygame

from source.constants import SCREEN_WIDTH
from source.state.state_machine import GameState, StateMachine
from source.utils.sprite_loader import load_image


class MenuState(GameState):
    """主菜单。"""

    def __init__(self, machine: StateMachine) -> None:
        super().__init__(machine)
        self._background: pygame.Surface | None = None
        self._font_btn: pygame.font.Font | None = None
        self._font_sub: pygame.font.Font | None = None
        self._button_rect: pygame.Rect | None = None

    def enter(self, *args, **kwargs) -> None:
        from source.utils.font_helper import get_font  # noqa: PLC0415

        try:
            self._background = load_image("Screen/MainMenu.png")
        except Exception:
            self._background = None

        self._font_btn = get_font(30, bold=True)
        self._font_sub = get_font(16)

        # 按钮居中放置
        self._button_rect = pygame.Rect(370, 520, 160, 55)

    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.machine.clear(); return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.machine.clear(); return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._button_rect and self._button_rect.collidepoint(event.pos):
                from source.state.level_state import LevelState  # noqa: PLC0415
                self.machine.push(LevelState(self.machine))

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        if self._background:
            screen.blit(self._background, (0, 0))
        else:
            screen.fill((30, 30, 60))

        if self._font_btn and self._button_rect:
            mx, my = pygame.mouse.get_pos()
            hover = self._button_rect.collidepoint(mx, my)

            # 墓碑风格按钮文字
            color = (255, 230, 150) if hover else (180, 150, 100)
            shadow_c = (20, 15, 5)

            label = self._font_btn.render("无尽模式", True, color)
            lr = label.get_rect(center=self._button_rect.center)
            # 阴影
            s = self._font_btn.render("无尽模式", True, shadow_c)
            screen.blit(s, (lr.x + 2, lr.y + 2))
            screen.blit(label, lr)

            if hover:
                line_y = self._button_rect.centery + 24
                pygame.draw.line(screen, (200, 170, 100),
                                 (self._button_rect.centerx - 50, line_y),
                                 (self._button_rect.centerx + 50, line_y), 1)

        if self._font_sub:
            h = self._font_sub.render("点击开始  |  ESC 退出", True, (120, 120, 140))
            hr = h.get_rect(center=(SCREEN_WIDTH // 2, 580))
            screen.blit(h, hr)
