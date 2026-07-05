"""碰撞检测系统。"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from source.entity.bullet import Bullet
    from source.entity.plant import Plant
    from source.entity.zombie import Zombie


class CollisionSystem:
    """处理子弹×僵尸的碰撞检测。

    僵尸×植物的碰撞由僵尸自身的 update 处理（walk 时检测重叠）。
    """

    @staticmethod
    def check_bullet_zombie(
        bullets: list[Bullet],
        zombies: list[Zombie],
    ) -> None:
        """检测所有子弹与僵尸的碰撞。命中后子弹和僵尸各扣 HP。"""
        for bullet in bullets:
            if not bullet.alive:
                continue
            for zombie in zombies:
                if not zombie.alive:
                    continue
                if bullet.row != zombie.row:
                    continue
                if bullet.rect.colliderect(zombie.rect):
                    zombie.take_damage(bullet.damage)
                    # 冰冻弹施加减速
                    if hasattr(bullet, "apply_slow"):
                        bullet.apply_slow(zombie)
                    bullet.alive = False
                    break
