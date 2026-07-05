"""无尽模式关卡 — 僵尸不断生成，难度递增，直到防线被突破。"""

from __future__ import annotations

import random

import pygame

from source.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_COLS, GRID_ROWS,
    GRID_X_SIZE, GRID_Y_SIZE, MAP_OFFSET_X, MAP_OFFSET_Y, COLOR_WHITE,
)
from source.entity.bullet import Bullet
from source.entity.lawnmower import LawnMower
from source.entity.plant import (
    CherryBomb, PeaShooter, Plant, PotatoMine, Repeater, SnowPea, SunFlower, WallNut,
)
from source.entity.sun import Sun
from source.entity.zombie import (
    NormalZombie, ConeheadZombie, BucketheadZombie, FlagZombie, Zombie,
)
from source.map.grid_map import GridMap
from source.state.state_machine import GameState, StateMachine
from source.system.collision import CollisionSystem
from source.system.sun_manager import SunManager
from source.ui.card_panel import CardPanel
from source.utils.sprite_loader import load_image

# ── 常量 ──────────────────────────────────────────────

ALL_CARD_TYPES = ["sunflower", "peashooter", "wallnut", "cherrybomb",
                   "potatomine", "snowpea", "repeater"]

_PLANT_FACTORY: dict[str, type[Plant]] = {
    "sunflower": SunFlower, "peashooter": PeaShooter, "wallnut": WallNut,
    "cherrybomb": CherryBomb, "potatomine": PotatoMine,
    "snowpea": SnowPea, "repeater": Repeater,
}

# 可种植范围：列 0-7（col 8 是道路，不可种植），行 0-4 全部
VALID_COL_MIN = 0
VALID_COL_MAX = 7
VALID_ROW_MIN = 0
VALID_ROW_MAX = 4

# 僵尸类型池（无尽模式权重）
_ZOMBIE_POOL = [
    (NormalZombie, 10),
    (ConeheadZombie, 5),
    (BucketheadZombie, 2),
    (FlagZombie, 2),
]


class LevelState(GameState):
    """无尽模式游戏状态。"""

    def __init__(self, machine: StateMachine) -> None:
        super().__init__(machine)
        self._grid_map = GridMap()
        self._sun_manager = SunManager()
        self._collision = CollisionSystem()
        self._card_panel: CardPanel | None = None
        self._lawnmowers: list[LawnMower] = []
        self._plants: list[Plant] = []
        self._zombies: list[Zombie] = []
        self._bullets: list[Bullet] = []
        self._suns: list[Sun] = []
        self._selected_plant: str | None = None
        self._dragging = False          # 是否正在拖放
        self._mouse_pos = (0, 0)
        self._background: pygame.Surface | None = None
        self._font: pygame.font.Font | None = None
        self._font_small: pygame.font.Font | None = None
        self._game_over = False
        self._paused = False
        self._pause_rect = pygame.Rect(0, 0, 0, 0)
        # 无尽模式数据
        self._score = 0
        self._elapsed = 0.0
        self._zombie_timer = 0.0
        self._spawn_interval = 6.0   # 初始间隔
        self._difficulty = 1

    # ── 生命周期 ──────────────────────────────────────

    def enter(self, *args, **kwargs) -> None:
        from source.utils.font_helper import get_font  # noqa: PLC0415
        self._font = get_font(24)
        self._font_small = get_font(16)

        try:
            bg = load_image("Items/Background/Background_0.jpg")
            self._background = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception:
            self._background = None

        self._reset_game()

    def exit(self) -> None:
        pass

    def _reset_game(self) -> None:
        self._plants.clear(); self._zombies.clear(); self._bullets.clear()
        self._suns.clear(); self._lawnmowers.clear()
        self._sun_manager = SunManager()
        self._card_panel = CardPanel(ALL_CARD_TYPES)
        self._selected_plant = None
        self._dragging = False
        self._game_over = False
        self._paused = False
        self._score = 0
        self._elapsed = 0.0
        self._zombie_timer = 3.0  # 3 秒后出第一只
        self._spawn_interval = 6.0
        self._difficulty = 1
        for row in range(GRID_ROWS):
            self._lawnmowers.append(LawnMower(row))

    # ── 输入 ──────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.machine.clear(); return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self._game_over: self.machine.pop(); return
                self._paused = not self._paused; return
            if event.key == pygame.K_r and self._game_over:
                self._reset_game(); return
        if self._game_over: return

        # 暂停 → 只响应暂停面板点击
        if self._paused:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_pause_click(event.pos)
            return

        if event.type == pygame.MOUSEMOTION:
            self._mouse_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._on_mouse_down(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._on_mouse_up(event.pos)

    def _on_mouse_down(self, pos: tuple[int, int]) -> None:
        # 暂停按钮
        if self._pause_rect.collidepoint(pos):
            self._paused = True; return
        # 收集阳光
        for sun in self._suns:
            if sun.alive and not sun.collected and sun.hit_test(pos):
                self._sun_manager.add(sun.collect()); return

        # 点击卡片 → 选中 + 开始拖放
        if self._card_panel:
            c = self._card_panel.get_clicked(pos)
            if c is not None:
                card = self._card_panel.get_card(c)
                if card and self._sun_manager.can_afford(card.sun_cost) and card.is_ready:
                    self._selected_plant = c
                    self._dragging = True
                return

    def _on_mouse_up(self, pos: tuple[int, int]) -> None:
        if not self._dragging or self._selected_plant is None:
            return
        self._dragging = False
        # 尝试在释放位置种植
        gp = GridMap.screen_to_grid(*pos)
        if gp and self._can_plant_at(*gp):
            self._place_plant(*gp)
        self._selected_plant = None

    # ── 主更新 ────────────────────────────────────────

    def update(self, dt: float) -> None:
        if self._game_over or self._paused: return
        self._elapsed += dt

        if self._card_panel: self._card_panel.update(dt)
        ns = self._sun_manager.update(dt); self._suns.extend(ns)
        for s in self._suns: s.update(dt)
        for p in self._plants:
            p.update(dt, bullets=self._bullets, suns=self._suns, zombies=self._zombies)
        for b in self._bullets: b.update(dt)
        self._update_endless_spawn(dt)
        for z in self._zombies: z.update(dt, plants=self._plants)
        self._collision.check_bullet_zombie(self._bullets, self._zombies)
        for m in self._lawnmowers: m.check_trigger(self._zombies); m.update(dt, zombies=self._zombies)
        self._cleanup(); self._check_lose()

    # ── 无尽僵尸生成 ──────────────────────────────────

    def _update_endless_spawn(self, dt: float) -> None:
        self._zombie_timer -= dt
        if self._zombie_timer <= 0:
            self._spawn_zombie()
            # 间隔递减，难度递增
            self._spawn_interval = max(1.5, 6.0 - self._elapsed / 60.0)
            self._zombie_timer = self._spawn_interval * random.uniform(0.7, 1.3)

    def _spawn_zombie(self) -> None:
        row = random.randint(0, GRID_ROWS - 1)

        # 根据经过时间选择僵尸类型（越后面越难）
        weights = _ZOMBIE_POOL.copy()
        if self._elapsed > 60:
            weights = [(NormalZombie, 5), (ConeheadZombie, 4),
                        (BucketheadZombie, 3), (FlagZombie, 3)]
        if self._elapsed > 120:
            weights = [(NormalZombie, 3), (ConeheadZombie, 3),
                        (BucketheadZombie, 4), (FlagZombie, 4)]

        total = sum(w for _, w in weights)
        r = random.randint(1, total)
        cumulative = 0
        z_type = NormalZombie
        for z_cls, w in weights:
            cumulative += w
            if r <= cumulative:
                z_type = z_cls
                break

        spawn_x = MAP_OFFSET_X + GRID_COLS * GRID_X_SIZE + 20
        spawn_y = MAP_OFFSET_Y + row * GRID_Y_SIZE + (GRID_Y_SIZE - 80) // 2
        self._zombies.append(z_type(x=spawn_x, y=spawn_y, row=row))

    # ── 种植 ──────────────────────────────────────────

    def _can_plant_at(self, col: int, row: int) -> bool:
        # 限定种植范围（草坪区域，不含道路和屋顶）
        if col < VALID_COL_MIN or col > VALID_COL_MAX:
            return False
        if row < VALID_ROW_MIN or row > VALID_ROW_MAX:
            return False
        for p in self._plants:
            if p.row == row and p.col == col and p.alive:
                return False
        if not self._selected_plant or not self._card_panel: return False
        card = self._card_panel.get_card(self._selected_plant)
        return card is not None and self._sun_manager.can_afford(card.sun_cost) and card.is_ready

    def _place_plant(self, col: int, row: int) -> None:
        f = _PLANT_FACTORY.get(self._selected_plant or "")
        if not f or not self._card_panel: return
        card = self._card_panel.get_card(self._selected_plant)  # type: ignore[arg-type]
        if not card: return
        self._sun_manager.spend(card.sun_cost); card.start_cooldown()
        cx, cy = GridMap.grid_center(col, row)
        self._plants.append(f(x=cx - 35, y=cy - 37, row=row, col=col))

    # ── 清理 / 失败判定 ───────────────────────────────

    def _cleanup(self) -> None:
        # 统计击杀
        for z in self._zombies:
            if not z.alive:
                self._score += 1
        self._plants = [p for p in self._plants if p.alive]
        self._zombies = [z for z in self._zombies if z.alive]
        self._bullets = [b for b in self._bullets if b.alive]
        self._suns = [s for s in self._suns if s.alive and not s.collected]

    def _check_lose(self) -> None:
        for z in self._zombies:
            if z.alive and z.rect.right < MAP_OFFSET_X - 40:
                self._game_over = True; return

    # ── 渲染 ──────────────────────────────────────────

    def draw(self, screen: pygame.Surface) -> None:
        if self._background: screen.blit(self._background, (0, 0))
        else: screen.fill((100, 149, 237))
        self._grid_map.draw(screen)
        for p in self._plants: p.draw(screen)
        for z in self._zombies: z.draw(screen)
        for b in self._bullets: b.draw(screen)
        for s in self._suns: s.draw(screen)
        for m in self._lawnmowers: m.draw(screen)
        self._draw_top_bar(screen)
        if self._card_panel: self._card_panel.draw(screen, self._sun_manager.sun_value)
        self._draw_drag_preview(screen)
        if self._game_over: self._draw_game_over(screen)
        if self._paused: self._draw_pause_panel(screen)

    def _draw_top_bar(self, screen: pygame.Surface) -> None:
        bar_h = 92
        bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, bar_h)
        pygame.draw.rect(screen, (49, 0, 0), bar_rect)
        for y_off in range(4, bar_h - 4, 6):
            alpha = 30 if y_off % 12 == 0 else 15
            stripe = pygame.Surface((SCREEN_WIDTH, 3), pygame.SRCALPHA)
            stripe.fill((104, 47, 17, alpha))
            screen.blit(stripe, (0, y_off))
        pygame.draw.line(screen, (104, 47, 17), (0, bar_h - 2), (SCREEN_WIDTH, bar_h - 2), 2)
        pygame.draw.line(screen, (30, 0, 0), (0, bar_h - 1), (SCREEN_WIDTH, bar_h - 1), 1)

        # 阳光
        sun_cx, sun_cy = 50, bar_h // 2
        glow = pygame.Surface((56, 56), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 240, 100, 100), (28, 28), 24)
        pygame.draw.circle(glow, (255, 220, 50, 180), (28, 28), 18)
        screen.blit(glow, (sun_cx - 28, sun_cy - 28))
        if self._font:
            v = self._font.render(str(self._sun_manager.sun_value), True, (50, 20, 0))
            vr = v.get_rect(center=(sun_cx, sun_cy))
            screen.blit(v, vr)

        # 击杀数 + 时间
        if self._font_small:
            sc = self._font_small.render(f"击杀: {self._score}", True, (220, 200, 160))
            sc_r = sc.get_rect()
            sc_r.topright = (SCREEN_WIDTH - 12, 8)
            screen.blit(sc, sc_r)
            tm = self._font_small.render(
                f"时间: {int(self._elapsed // 60)}:{int(self._elapsed % 60):02d}",
                True, (180, 160, 130),
            )
            tm_r = tm.get_rect()
            tm_r.topright = (SCREEN_WIDTH - 12, 26)
            screen.blit(tm, tm_r)

        # 暂停按钮
        btn_size = 36
        self._pause_rect = pygame.Rect(SCREEN_WIDTH - 100, 42, btn_size + 20, btn_size)
        mx, my = pygame.mouse.get_pos()
        hover = self._pause_rect.collidepoint(mx, my)
        btn_color = (160, 140, 100) if hover else (120, 100, 70)
        pygame.draw.rect(screen, btn_color, self._pause_rect, border_radius=4)
        pygame.draw.rect(screen, (80, 60, 40), self._pause_rect, width=2, border_radius=4)
        # 双竖线暂停图标
        bar_x = self._pause_rect.centerx - 6
        bar_y = self._pause_rect.centery - 8
        pygame.draw.rect(screen, (255, 255, 255), (bar_x - 4, bar_y, 5, 16))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x + 5, bar_y, 5, 16))

    def _draw_drag_preview(self, screen: pygame.Surface) -> None:
        """拖放种植预览。"""
        if not self._dragging or self._selected_plant is None:
            return
        gp = GridMap.screen_to_grid(*self._mouse_pos)
        if gp and self._can_plant_at(*gp):
            col, row = gp
            x, y = GridMap.grid_to_screen(col, row)
            pv = pygame.Surface((GRID_X_SIZE, GRID_Y_SIZE), pygame.SRCALPHA)
            pv.fill((0, 255, 0, 60))
            screen.blit(pv, (x, y))
        elif gp:
            # 不可种植区域显示红色
            col, row = gp
            x, y = GridMap.grid_to_screen(col, row)
            pv = pygame.Surface((GRID_X_SIZE, GRID_Y_SIZE), pygame.SRCALPHA)
            pv.fill((255, 0, 0, 40))
            screen.blit(pv, (x, y))

    def _draw_game_over(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        if self._font:
            t1 = self._font.render("游戏结束", True, (255, 80, 80))
            r1 = t1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(t1, r1)
            t2 = self._font.render(
                f"击杀 {self._score} 只僵尸 | 坚持了 {int(self._elapsed)} 秒",
                True, (255, 255, 255),
            )
            r2 = t2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(t2, r2)
        if self._font_small:
            h = self._font_small.render("按 R 重新开始 | ESC 返回菜单", True, (200, 200, 200))
            hr = h.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            screen.blit(h, hr)

    # ── 暂停面板 ──────────────────────────────────────

    _pause_buttons: list[tuple[pygame.Rect, str]] = []  # 动态生成

    def _draw_pause_panel(self, screen: pygame.Surface) -> None:
        """绘制暂停覆盖面板。"""
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        if not self._font:
            return

        # 标题
        title = self._font.render("游戏暂停", True, (255, 200, 100))
        tr = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title, tr)

        # 三个按钮
        btn_w, btn_h = 220, 50
        labels = ["继续游戏", "重新开始", "返回菜单"]
        self._pause_buttons.clear()
        for i, label in enumerate(labels):
            rect = pygame.Rect(
                (SCREEN_WIDTH - btn_w) // 2,
                SCREEN_HEIGHT // 2 - 30 + i * (btn_h + 16),
                btn_w, btn_h,
            )
            self._pause_buttons.append((rect, label))
            mx, my = pygame.mouse.get_pos()
            hover = rect.collidepoint(mx, my)
            bg_c = (80, 130, 60) if hover else (50, 90, 40)
            pygame.draw.rect(screen, bg_c, rect, border_radius=8)
            pygame.draw.rect(screen, (30, 60, 20), rect, width=2, border_radius=8)
            t = self._font.render(label, True, (255, 255, 255))
            tr2 = t.get_rect(center=rect.center)
            screen.blit(t, tr2)

        # 提示
        if self._font_small:
            hint = self._font_small.render("ESC 也可继续游戏", True, (160, 160, 160))
            hr2 = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140))
            screen.blit(hint, hr2)

    def _handle_pause_click(self, pos: tuple[int, int]) -> None:
        """处理暂停面板上的点击。"""
        for rect, label in self._pause_buttons:
            if rect.collidepoint(pos):
                if label == "继续游戏":
                    self._paused = False
                elif label == "重新开始":
                    self._reset_game()
                elif label == "返回菜单":
                    self.machine.pop()
                return
