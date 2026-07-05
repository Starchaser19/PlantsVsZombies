"""植物实体 — 基类 + 7 种子类（真实精灵渲染）。"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from source.entity.game_object import GameObject
from source.utils.animation import Animation
from source.utils.sprite_loader import load_frames, load_image

if TYPE_CHECKING:
    from source.entity.bullet import Bullet
    from source.entity.sun import Sun
    from source.entity.zombie import Zombie


class Plant(GameObject):
    """植物基类。"""

    def __init__(
        self,
        x: float,
        y: float,
        row: int,
        col: int,
        plant_type: str,
        hp: int = 300,
        sun_cost: int = 0,
        cooldown: float = 7.5,
    ) -> None:
        super().__init__(x, y, 70, 74, hp)
        self.row = row
        self.col = col
        self.plant_type = plant_type
        self.sun_cost = sun_cost
        self.cooldown = cooldown
        self._anim: Animation | None = None

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return
        if self._anim is not None:
            img = self._anim.current_frame
            img_rect = img.get_rect(center=self.rect.center)
            screen.blit(img, img_rect)
        _draw_hp_bar(screen, self)

    def _load_frames(self, directory: str, prefix: str | None = None) -> list[pygame.Surface]:
        """加载精灵帧序列。"""
        if prefix is None:
            prefix = self.plant_type
        return load_frames(f"Plants/{directory}", prefix)

    def _setup_anim(self, frames: list[pygame.Surface], duration: float = 0.12) -> None:
        self._anim = Animation(frames, frame_duration=duration)


# ── 经济植物 ──────────────────────────────────────────

class SunFlower(Plant):
    """向日葵 — 每隔 sun_interval 秒产出一个阳光。"""

    SUN_INTERVAL = 6.0
    SUN_VALUE = 25

    _frames: list[pygame.Surface] | None = None

    def __init__(self, x: float, y: float, row: int, col: int) -> None:
        super().__init__(
            x=x, y=y, row=row, col=col,
            plant_type="sunflower", hp=300, sun_cost=50, cooldown=7.5,
        )
        self._sun_timer = self.SUN_INTERVAL
        if SunFlower._frames is None:
            SunFlower._frames = load_frames("Plants/SunFlower", "SunFlower")
        self._setup_anim(SunFlower._frames)

    def update(self, dt: float, **kwargs) -> None:
        if not self.alive:
            return
        if self._anim:
            self._anim.update(dt)
        suns: list[Sun] = kwargs.get("suns", [])
        self._sun_timer -= dt
        if self._sun_timer <= 0:
            self._sun_timer += self.SUN_INTERVAL
            from source.entity.sun import Sun  # noqa: PLC0415
            sun = Sun(x=self.rect.centerx, y=self.rect.top - 20, value=self.SUN_VALUE)
            suns.append(sun)


# ── 攻击植物 ──────────────────────────────────────────

class PeaShooter(Plant):
    """豌豆射手 — 单发豌豆。"""

    SHOOT_INTERVAL = 1.5
    BULLET_DAMAGE = 20

    _frames: list[pygame.Surface] | None = None

    def __init__(self, x: float, y: float, row: int, col: int) -> None:
        super().__init__(
            x=x, y=y, row=row, col=col,
            plant_type="peashooter", hp=300, sun_cost=100, cooldown=7.5,
        )
        self._shoot_timer = 0.5
        if PeaShooter._frames is None:
            PeaShooter._frames = load_frames("Plants/Peashooter", "Peashooter")
        self._setup_anim(PeaShooter._frames)

    def update(self, dt: float, **kwargs) -> None:
        if not self.alive:
            return
        if self._anim:
            self._anim.update(dt)
        bullets: list[Bullet] = kwargs.get("bullets", [])
        zombies: list[Zombie] = kwargs.get("zombies", [])

        if not any(z.row == self.row and z.alive for z in zombies):
            return

        self._shoot_timer -= dt
        if self._shoot_timer <= 0:
            self._shoot_timer += self.SHOOT_INTERVAL
            from source.entity.bullet import PeaBullet  # noqa: PLC0415
            bullet = PeaBullet(
                x=self.rect.right - 10, y=self.rect.centery - 15,
                row=self.row, damage=self.BULLET_DAMAGE,
            )
            bullets.append(bullet)


class SnowPea(Plant):
    """寒冰射手 — 发射冰冻豌豆（减速僵尸）。"""

    SHOOT_INTERVAL = 1.5
    BULLET_DAMAGE = 20
    SLOW_DURATION = 3.0  # 减速持续秒数

    _frames: list[pygame.Surface] | None = None

    def __init__(self, x: float, y: float, row: int, col: int) -> None:
        super().__init__(
            x=x, y=y, row=row, col=col,
            plant_type="snowpea", hp=300, sun_cost=175, cooldown=7.5,
        )
        self._shoot_timer = 0.5
        if SnowPea._frames is None:
            SnowPea._frames = load_frames("Plants/SnowPea", "SnowPea")
        self._setup_anim(SnowPea._frames)

    def update(self, dt: float, **kwargs) -> None:
        if not self.alive:
            return
        if self._anim:
            self._anim.update(dt)
        bullets: list[Bullet] = kwargs.get("bullets", [])
        zombies: list[Zombie] = kwargs.get("zombies", [])

        if not any(z.row == self.row and z.alive for z in zombies):
            return

        self._shoot_timer -= dt
        if self._shoot_timer <= 0:
            self._shoot_timer += self.SHOOT_INTERVAL
            from source.entity.bullet import SnowPeaBullet  # noqa: PLC0415
            bullet = SnowPeaBullet(
                x=self.rect.right - 10, y=self.rect.centery - 15,
                row=self.row, damage=self.BULLET_DAMAGE,
                slow_duration=self.SLOW_DURATION,
            )
            bullets.append(bullet)


class Repeater(Plant):
    """双发射手 — 每次发射 2 颗豌豆。"""

    SHOOT_INTERVAL = 1.5
    BULLET_DAMAGE = 20

    _frames: list[pygame.Surface] | None = None

    def __init__(self, x: float, y: float, row: int, col: int) -> None:
        super().__init__(
            x=x, y=y, row=row, col=col,
            plant_type="repeater", hp=300, sun_cost=200, cooldown=7.5,
        )
        self._shoot_timer = 0.5
        if Repeater._frames is None:
            Repeater._frames = load_frames("Plants/RepeaterPea", "RepeaterPea")
        self._setup_anim(Repeater._frames)

    def update(self, dt: float, **kwargs) -> None:
        if not self.alive:
            return
        if self._anim:
            self._anim.update(dt)
        bullets: list[Bullet] = kwargs.get("bullets", [])
        zombies: list[Zombie] = kwargs.get("zombies", [])

        if not any(z.row == self.row and z.alive for z in zombies):
            return

        self._shoot_timer -= dt
        if self._shoot_timer <= 0:
            self._shoot_timer += self.SHOOT_INTERVAL
            from source.entity.bullet import PeaBullet  # noqa: PLC0415
            # 发射两颗子弹（第二颗延迟 0.1s 不会太挤）
            for offset in (0, 15):
                bullet = PeaBullet(
                    x=self.rect.right - 10 + offset,
                    y=self.rect.centery - 15,
                    row=self.row, damage=self.BULLET_DAMAGE,
                )
                bullets.append(bullet)


# ── 防御植物 ──────────────────────────────────────────

class WallNut(Plant):
    """坚果墙 — 高血量防御植物。"""

    HP_FULL = 4000
    HP_CRACKED1 = 2666   # 2/3
    HP_CRACKED2 = 1333   # 1/3

    _frames: dict[str, list[pygame.Surface]] | None = None

    def __init__(self, x: float, y: float, row: int, col: int) -> None:
        super().__init__(
            x=x, y=y, row=row, col=col,
            plant_type="wallnut", hp=self.HP_FULL, sun_cost=50, cooldown=30.0,
        )
        if WallNut._frames is None:
            WallNut._frames = {
                "full": load_frames("Plants/WallNut/WallNut", "WallNut"),
                "cracked1": load_frames("Plants/WallNut/WallNut_cracked1", "WallNut_cracked1"),
                "cracked2": load_frames("Plants/WallNut/WallNut_cracked2", "WallNut_cracked2"),
            }
        self._setup_anim(WallNut._frames["full"])

    def update(self, dt: float, **kwargs) -> None:
        if not self.alive:
            return
        if self._anim:
            self._anim.update(dt)
        # 根据 HP 切换外观
        if WallNut._frames:
            if self.hp <= self.HP_CRACKED2:
                self._anim = Animation(WallNut._frames["cracked2"], frame_duration=0.15)
            elif self.hp <= self.HP_CRACKED1:
                self._anim = Animation(WallNut._frames["cracked1"], frame_duration=0.15)


# ── 爆炸植物 ──────────────────────────────────────────

class CherryBomb(Plant):
    """樱桃炸弹 — 放置后延迟 1s 引爆 3×3 范围。"""

    DAMAGE = 1800
    EXPLODE_RADIUS = 1  # 3×3 格
    FUSE_TIME = 1.0     # 引爆延迟

    _frames: list[pygame.Surface] | None = None

    def __init__(self, x: float, y: float, row: int, col: int) -> None:
        super().__init__(
            x=x, y=y, row=row, col=col,
            plant_type="cherrybomb", hp=1, sun_cost=150, cooldown=50.0,
        )
        self._fuse_timer = self.FUSE_TIME
        self._exploded = False
        if CherryBomb._frames is None:
            CherryBomb._frames = load_frames("Plants/CherryBomb", "CherryBomb")
        self._setup_anim(CherryBomb._frames, duration=0.15)

    def update(self, dt: float, **kwargs) -> None:
        if not self.alive or self._exploded:
            return
        if self._anim:
            self._anim.update(dt)

        self._fuse_timer -= dt
        if self._fuse_timer <= 0:
            self._explode(kwargs.get("zombies", []))

    def _explode(self, zombies: list[Zombie]) -> None:
        self._exploded = True
        r = self.EXPLODE_RADIUS
        for zombie in zombies:
            if not zombie.alive:
                continue
            if (abs(zombie.row - self.row) <= r
                    and abs(zombie.col - self.col) <= r):
                zombie.take_damage(self.DAMAGE)
        self.alive = False


class PotatoMine(Plant):
    """土豆地雷 — 15s 激活后，僵尸踩踏引爆。"""

    DAMAGE = 1800
    ARM_TIME = 15.0
    EXPLODE_RADIUS = 1

    _frames_init: list[pygame.Surface] | None = None
    _frames_active: list[pygame.Surface] | None = None
    _image_explode: pygame.Surface | None = None

    def __init__(self, x: float, y: float, row: int, col: int) -> None:
        super().__init__(
            x=x, y=y, row=row, col=col,
            plant_type="potatomine", hp=300, sun_cost=25, cooldown=30.0,
        )
        self._armed = False
        self._arm_timer = self.ARM_TIME
        self._exploded = False

        if PotatoMine._frames_init is None:
            PotatoMine._frames_init = load_frames(
                "Plants/PotatoMine/PotatoMineInit", "PotatoMineInit"
            )
            PotatoMine._frames_active = load_frames(
                "Plants/PotatoMine/PotatoMine", "PotatoMine"
            )
        # 初始状态：未激活（小土堆）
        if PotatoMine._frames_init:
            if len(PotatoMine._frames_init) == 1:
                # 单帧Init，做暗色底衬去白边
                self._init_img = PotatoMine._frames_init[0]
            self._setup_anim(PotatoMine._frames_init, duration=1.0)
        else:
            self._init_img = None

    def update(self, dt: float, **kwargs) -> None:
        if not self.alive or self._exploded:
            return
        if self._anim:
            self._anim.update(dt)

        # 激活倒计时
        if not self._armed:
            self._arm_timer -= dt
            if self._arm_timer <= 0:
                self._armed = True
                if PotatoMine._frames_active:
                    self._setup_anim(PotatoMine._frames_active)
            return

        # 激活后：检测僵尸踩踏
        zombies: list[Zombie] = kwargs.get("zombies", [])
        for zombie in zombies:
            if not zombie.alive:
                continue
            if zombie.row == self.row and self.rect.colliderect(zombie.rect):
                self._explode(zombies)
                return

    def _explode(self, zombies: list[Zombie]) -> None:
        self._exploded = True
        r = self.EXPLODE_RADIUS
        for zombie in zombies:
            if not zombie.alive:
                continue
            if abs(zombie.row - self.row) <= r:
                # 简单范围判定（同列附近）
                if abs(zombie.rect.centerx - self.rect.centerx) < 120:
                    zombie.take_damage(self.DAMAGE)
        self.alive = False

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive or self._exploded:
            return
        # 暗色圆形底衬（掩盖精灵白边）
        cx, cy = self.rect.centerx, self.rect.centery + 2
        pygame.draw.ellipse(screen, (35, 25, 12),
                            (cx - 22, cy - 12, 44, 28))
        if self._anim is not None:
            img = self._anim.current_frame
            img_rect = img.get_rect(center=self.rect.center)
            screen.blit(img, img_rect)
        _draw_hp_bar(screen, self)


# ── 工具 ──────────────────────────────────────────────

def _draw_hp_bar(screen: pygame.Surface, plant: Plant) -> None:
    if plant.hp >= plant.max_hp:
        return
    bar_w = plant.rect.width - 6
    bar_h = 3
    bar_x = plant.rect.x + 3
    bar_y = plant.rect.bottom + 1
    # 背景
    pygame.draw.rect(screen, (60, 60, 60), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
    # 红色底
    pygame.draw.rect(screen, (180, 30, 30), (bar_x, bar_y, bar_w, bar_h))
    # 绿色当前值
    green_w = int(bar_w * plant.hp_ratio)
    if green_w > 0:
        pygame.draw.rect(screen, (50, 220, 50), (bar_x, bar_y, green_w, bar_h))
