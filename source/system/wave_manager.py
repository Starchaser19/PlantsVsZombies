"""波次管理器 — 从 JSON 配置加载并按时生成僵尸。"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from source.constants import GRID_COLS, GRID_ROWS, GRID_X_SIZE, MAP_OFFSET_X, MAP_OFFSET_Y, GRID_Y_SIZE
from source.entity.zombie import (
    NormalZombie,
    ConeheadZombie,
    BucketheadZombie,
    FlagZombie,
    Zombie,
)

_ZOMBIE_FACTORY: dict[str, type[Zombie]] = {
    "normal": NormalZombie,
    "conehead": ConeheadZombie,
    "buckethead": BucketheadZombie,
    "flag": FlagZombie,
}

_LEVELS_DIR = Path(__file__).parent.parent / "data" / "levels"


class WaveManager:
    """管理关卡僵尸波次生成。"""

    def __init__(self, level_id: int) -> None:
        self.level_id = level_id
        self._config = self._load_level(level_id)
        self._elapsed = 0.0
        self._current_wave = 0
        self._zombie_index = 0    # 当前波次中的僵尸条目索引
        self._batch_spawned = 0   # 当前条目已生成的僵尸数量（count > 1 时）
        self._announce_timer = 0.0
        self._announce_text = ""
        self._all_spawned = False

    # ── 属性 ──────────────────────────────────────────

    @property
    def level_name(self) -> str:
        return self._config.get("name", f"关卡 {self.level_id}")

    @property
    def init_sun(self) -> int:
        return self._config.get("init_sun", 50)

    @property
    def plant_cards(self) -> list[str]:
        return self._config.get("plant_cards", ["sunflower", "peashooter"])

    @property
    def background_path(self) -> str:
        return self._config.get("background", "Items/Background/Background_0.jpg")

    @property
    def announce_text(self) -> str:
        return self._announce_text

    @property
    def is_announcing(self) -> bool:
        return self._announce_timer > 0

    @property
    def all_spawned(self) -> bool:
        return self._all_spawned

    # ── 更新 ──────────────────────────────────────────

    def update(self, dt: float) -> list[Zombie]:
        """更新波次计时，返回本帧应生成的新僵尸列表。"""
        self._elapsed += dt

        if self._announce_timer > 0:
            self._announce_timer -= dt

        new_zombies: list[Zombie] = []

        waves = self._config.get("waves", [])
        if self._current_wave >= len(waves):
            self._all_spawned = True
            return new_zombies

        wave = waves[self._current_wave]
        wave_start = self._wave_start_time(self._current_wave)
        wave_elapsed = (self._elapsed - wave_start) * 1000

        # 波次通告
        if (wave.get("announce")
                and not self._announce_timer
                and self._zombie_index == 0
                and self._batch_spawned == 0
                and wave_elapsed >= -500):
            self._announce_text = wave.get("announce_text", "一大波僵尸正在逼近！")
            self._announce_timer = 2.0

        zombies = wave.get("zombies", [])

        # 按时间线生成僵尸
        while self._zombie_index < len(zombies):
            entry = zombies[self._zombie_index]
            spawn_time_ms = entry.get("time", 0) * 1000
            count = entry.get("count", 1)
            interval = entry.get("interval", 0)
            row_spec = entry.get("row", -1)
            z_type = entry.get("type", "normal")

            # 计算第 _batch_spawned 个僵尸的实际生成时间
            if interval > 0 and self._batch_spawned > 0:
                actual_spawn_time = spawn_time_ms + self._batch_spawned * interval
            else:
                actual_spawn_time = spawn_time_ms

            if wave_elapsed < actual_spawn_time:
                break  # 还没到生成时间

            # 生成一个僵尸
            row = row_spec if row_spec >= 0 else random.randint(0, GRID_ROWS - 1)
            zombie = self._create_zombie(z_type, row)
            new_zombies.append(zombie)
            self._batch_spawned += 1

            # 该条目的所有僵尸已生成完毕 → 移到下一个条目
            if self._batch_spawned >= count:
                self._zombie_index += 1
                self._batch_spawned = 0

        # 当前波次所有条目处理完毕 → 进入下一波
        if self._zombie_index >= len(zombies):
            self._current_wave += 1
            self._zombie_index = 0
            self._batch_spawned = 0
            if self._current_wave >= len(waves):
                self._all_spawned = True

        return new_zombies

    # ── 内部方法 ──────────────────────────────────────

    def _create_zombie(self, z_type: str, row: int) -> Zombie:
        factory = _ZOMBIE_FACTORY.get(z_type, NormalZombie)
        spawn_x = MAP_OFFSET_X + GRID_COLS * GRID_X_SIZE + 20
        spawn_y = MAP_OFFSET_Y + row * GRID_Y_SIZE + (GRID_Y_SIZE - 80) // 2
        return factory(x=spawn_x, y=spawn_y, row=row)

    def _wave_start_time(self, wave_index: int) -> float:
        """计算某一波的开始时间（秒）。"""
        total = 0.0
        for i in range(wave_index):
            wave = self._config["waves"][i]
            zs = wave.get("zombies", [])
            if zs:
                last = zs[-1]
                last_count = last.get("count", 1)
                last_interval = last.get("interval", 0)
                last_time = last.get("time", 0)
                # 最后一个条目的实际结束时间
                end_time = last_time + (last_count - 1) * max(last_interval, 0) / 1000
                total += end_time + 5
        return total

    @staticmethod
    def _load_level(level_id: int) -> dict[str, Any]:
        file_path = _LEVELS_DIR / f"level_{level_id:02d}.json"
        if not file_path.exists():
            file_path = _LEVELS_DIR / "level_01.json"
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def available_levels() -> list[int]:
        levels = []
        if _LEVELS_DIR.is_dir():
            import re
            for fname in sorted(_LEVELS_DIR.iterdir()):
                m = re.match(r"level_(\d+)\.json", fname.name)
                if m:
                    levels.append(int(m.group(1)))
        return levels
