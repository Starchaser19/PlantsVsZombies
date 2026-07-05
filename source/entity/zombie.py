"""僵尸实体 — 基类 + 4 种子类（WALK/ATTACK/DEATH 状态机 + 减速）。"""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

import pygame

from source.entity.game_object import GameObject
from source.utils.animation import Animator, Animation
from source.utils.sprite_loader import load_frames

if TYPE_CHECKING:
    from source.entity.plant import Plant


class ZombieState(Enum):
    WALK = auto()
    ATTACK = auto()
    DEATH = auto()


class Zombie(GameObject):
    """僵尸基类。"""

    def __init__(
        self,
        x: float,
        y: float,
        row: int,
        hp: int = 200,
        zombie_type: str = "normal",
    ) -> None:
        super().__init__(x, y, 55, 100, hp)
        self._fx = float(x)
        self.row = row
        self.zombie_type = zombie_type
        self.state = ZombieState.WALK
        self._attack_timer = 0.0
        self._attack_target: Plant | None = None
        self._animator: Animator | None = None

        # 减速状态
        self._slow_timer = 0.0
        self._slow_duration = 0.0

    # ── 属性 ──────────────────────────────────────────

    @property
    def is_slowed(self) -> bool:
        return self._slow_timer > 0

    @property
    def col(self) -> int:
        """僵尸所在网格列（由 x 坐标推算）。"""
        from source.map.grid_map import GridMap  # noqa: PLC0415
        result = GridMap.screen_to_grid(self.rect.centerx, self.rect.centery)
        return result[0] if result else -1

    # ── 可重写 ────────────────────────────────────────

    def _get_speed(self) -> float:
        return 15.0

    def _get_damage(self) -> float:
        return 100.0

    # ── 减速 ──────────────────────────────────────────

    def apply_slow(self, duration: float) -> None:
        """施加减速效果。可叠加刷新持续时间。"""
        self._slow_duration = duration
        self._slow_timer = duration

    # ── 更新 ──────────────────────────────────────────

    def update(self, dt: float, **kwargs) -> None:
        if not self.alive:
            return

        # 减速计时
        if self._slow_timer > 0:
            self._slow_timer -= dt
            if self._slow_timer <= 0:
                self._slow_timer = 0.0

        plants: list[Plant] = kwargs.get("plants", [])

        if self._animator:
            self._animator.update(dt)

        if self.state == ZombieState.DEATH:
            return
        if self.state == ZombieState.ATTACK:
            self._update_attack(dt, plants)
            return
        if self.state == ZombieState.WALK:
            self._update_walk(dt, plants)

    def _update_walk(self, dt: float, plants: list[Plant]) -> None:
        speed = self._get_speed()
        if self.is_slowed:
            speed *= 0.5
        self._fx -= speed * dt
        self.rect.x = int(self._fx)

        for plant in plants:
            if not plant.alive:
                continue
            if plant.row != self.row:
                continue
            if self.rect.colliderect(plant.rect):
                self.state = ZombieState.ATTACK
                self._attack_target = plant
                self._attack_timer = 0.0
                if self._animator:
                    self._animator.set_state("attack")
                return

    def _update_attack(self, dt: float, plants: list[Plant]) -> None:
        if self._attack_target is None or not self._attack_target.alive:
            self.state = ZombieState.WALK
            self._attack_target = None
            if self._animator:
                self._animator.set_state("walk")
            return

        attack_speed = 1.0
        if self.is_slowed:
            attack_speed = 0.5
        self._attack_timer += dt * attack_speed
        if self._attack_timer >= 1.0:
            self._attack_timer -= 1.0
            self._attack_target.take_damage(int(self._get_damage()))
            if not self._attack_target.alive:
                self.state = ZombieState.WALK
                self._attack_target = None
                if self._animator:
                    self._animator.set_state("walk")

    def _on_death(self) -> None:
        self.state = ZombieState.DEATH
        if self._animator:
            self._animator.set_state("die")

    # ── 渲染 ──────────────────────────────────────────

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return
        if self._animator is not None:
            img = self._animator.current_frame
            img_rect = img.get_rect(midbottom=self.rect.midbottom)
            screen.blit(img, img_rect)
            # 减速指示：头顶蓝色冰晶小圆点
            if self.is_slowed:
                ice_x, ice_y = img_rect.centerx, img_rect.top + 6
                pygame.draw.circle(screen, (80, 180, 255), (ice_x, ice_y), 6)
                pygame.draw.circle(screen, (180, 230, 255), (ice_x - 1, ice_y - 1), 2)

        # HP 条
        if self.hp < self.max_hp:
            bar_w = self.rect.width
            bar_h = 3
            bar_x = self.rect.x
            bar_y = self.rect.top - 6
            pygame.draw.rect(screen, (60, 60, 60), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
            pygame.draw.rect(screen, (180, 30, 30), (bar_x, bar_y, bar_w, bar_h))
            green_w = int(bar_w * self.hp_ratio)
            if green_w > 0:
                pygame.draw.rect(screen, (50, 220, 50), (bar_x, bar_y, green_w, bar_h))


# ── 僵尸子类 ──────────────────────────────────────────

class NormalZombie(Zombie):
    """普通僵尸。"""
    _anim_data: dict[str, list[pygame.Surface]] | None = None

    def __init__(self, x: float, y: float, row: int) -> None:
        super().__init__(x=x, y=y, row=row, hp=120, zombie_type="normal")
        self._setup_animator()

    @classmethod
    def _load_anim_data(cls) -> dict[str, list[pygame.Surface]]:
        if cls._anim_data is None:
            cls._anim_data = {
                "walk": load_frames("Zombies/NormalZombie/Zombie", "Zombie"),
                "attack": load_frames("Zombies/NormalZombie/ZombieAttack", "ZombieAttack"),
                "die": load_frames("Zombies/NormalZombie/ZombieDie", "ZombieDie"),
                "losthead": load_frames("Zombies/NormalZombie/ZombieLostHead", "ZombieLostHead"),
                "losthead_attack": load_frames(
                    "Zombies/NormalZombie/ZombieLostHeadAttack", "ZombieLostHeadAttack"
                ),
            }
        return cls._anim_data

    def _setup_animator(self) -> None:
        data = self._load_anim_data()
        self._animator = Animator({
            "walk": Animation(data["walk"], frame_duration=0.08),
            "attack": Animation(data["attack"], frame_duration=0.08),
            "die": Animation(data["die"], frame_duration=0.12, loop=False),
            "losthead": Animation(data["losthead"], frame_duration=0.08),
            "losthead_attack": Animation(data["losthead_attack"], frame_duration=0.08),
        }, initial_state="walk")


class ConeheadZombie(Zombie):
    """路障僵尸。"""
    _anim_data: dict[str, list[pygame.Surface]] | None = None

    def __init__(self, x: float, y: float, row: int) -> None:
        super().__init__(x=x, y=y, row=row, hp=350, zombie_type="conehead")
        self._setup_animator()

    @classmethod
    def _load_anim_data(cls) -> dict[str, list[pygame.Surface]]:
        if cls._anim_data is None:
            cls._anim_data = {
                "walk": load_frames("Zombies/ConeheadZombie/ConeheadZombie", "ConeheadZombie"),
                "attack": load_frames(
                    "Zombies/ConeheadZombie/ConeheadZombieAttack", "ConeheadZombieAttack"
                ),
            }
        return cls._anim_data

    def _setup_animator(self) -> None:
        data = self._load_anim_data()
        self._animator = Animator({
            "walk": Animation(data["walk"], frame_duration=0.08),
            "attack": Animation(data["attack"], frame_duration=0.08),
        }, initial_state="walk")


class BucketheadZombie(Zombie):
    """铁桶僵尸。"""
    _anim_data: dict[str, list[pygame.Surface]] | None = None

    def __init__(self, x: float, y: float, row: int) -> None:
        super().__init__(x=x, y=y, row=row, hp=800, zombie_type="buckethead")
        self._setup_animator()

    @classmethod
    def _load_anim_data(cls) -> dict[str, list[pygame.Surface]]:
        if cls._anim_data is None:
            cls._anim_data = {
                "walk": load_frames(
                    "Zombies/BucketheadZombie/BucketheadZombie", "BucketheadZombie"
                ),
                "attack": load_frames(
                    "Zombies/BucketheadZombie/BucketheadZombieAttack", "BucketheadZombieAttack"
                ),
            }
        return cls._anim_data

    def _setup_animator(self) -> None:
        data = self._load_anim_data()
        self._animator = Animator({
            "walk": Animation(data["walk"], frame_duration=0.08),
            "attack": Animation(data["attack"], frame_duration=0.08),
        }, initial_state="walk")


class FlagZombie(Zombie):
    """旗帜僵尸 — 移速稍快。"""
    _anim_data: dict[str, list[pygame.Surface]] | None = None

    def __init__(self, x: float, y: float, row: int) -> None:
        super().__init__(x=x, y=y, row=row, hp=120, zombie_type="flag")
        self._setup_animator()

    def _get_speed(self) -> float:
        return 22.0  # 比普通僵尸快

    @classmethod
    def _load_anim_data(cls) -> dict[str, list[pygame.Surface]]:
        if cls._anim_data is None:
            cls._anim_data = {
                "walk": load_frames("Zombies/FlagZombie/FlagZombie", "FlagZombie"),
                "attack": load_frames(
                    "Zombies/FlagZombie/FlagZombieAttack", "FlagZombieAttack"
                ),
            }
        return cls._anim_data

    def _setup_animator(self) -> None:
        data = self._load_anim_data()
        self._animator = Animator({
            "walk": Animation(data["walk"], frame_duration=0.08),
            "attack": Animation(data["attack"], frame_duration=0.08),
        }, initial_state="walk")
