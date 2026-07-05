"""精灵加载器 — 图片加载 + 缓存 + 帧序列读取。"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pygame

# ── 项目资源根目录 ──────────────────────────────────

_RESOURCES_DIR = Path(__file__).parent.parent.parent / "resources" / "graphics"


class SpriteLoader:
    """精灵资源加载器（单例模式）。

    自动缓存已加载的图片，避免重复 I/O。
    """

    _instance: SpriteLoader | None = None

    def __new__(cls) -> "SpriteLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache: dict[str, pygame.Surface] = {}
        return cls._instance

    # ── 公开 API ──────────────────────────────────────

    def load_image(self, relative_path: str) -> pygame.Surface:
        """加载单张图片（带透明通道）。

        Args:
            relative_path: 相对于 resources/graphics/ 的路径。
                           例如 "Plants/Peashooter/Peashooter_0.png"
        """
        if relative_path in self._cache:
            return self._cache[relative_path]

        full_path = _RESOURCES_DIR / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"精灵文件未找到: {full_path}")

        try:
            image = pygame.image.load(str(full_path)).convert_alpha()
        except pygame.error:
            # 部分图片无透明通道（如背景 .jpg）
            image = pygame.image.load(str(full_path)).convert()

        self._cache[relative_path] = image
        return image

    def load_frames(
        self,
        directory: str,
        prefix: str = "",
        scale: float = 1.0,
    ) -> list[pygame.Surface]:
        """加载目录下所有帧图片。

        Args:
            directory: 相对于 resources/graphics/ 的目录路径。
            prefix: 帧文件名前缀（不含 _N.png 部分）。
                    例如 prefix="Peashooter" 匹配 Peashooter_0.png, Peashooter_1.png, ...
            scale: 缩放因子（1.0 = 原始大小）。

        Returns:
            按编号排序的帧列表。若目录不存在则返回空列表。
        """
        full_dir = _RESOURCES_DIR / directory
        if not full_dir.is_dir():
            return []

        # 匹配 "prefix_N.png" 或 "prefix_N.jpg"
        pattern = re.compile(
            rf"^{re.escape(prefix)}_(\d+)\.(png|jpg|jpeg|PNG|JPG)$"
        )
        frames_info: list[tuple[int, str]] = []

        for fname in os.listdir(full_dir):
            m = pattern.match(fname)
            if m:
                frames_info.append((int(m.group(1)), fname))

        # 按帧编号排序
        frames_info.sort(key=lambda x: x[0])

        frames: list[pygame.Surface] = []
        for _, fname in frames_info:
            rel_path = f"{directory}/{fname}"
            img = self.load_image(rel_path)
            if scale != 1.0:
                w = int(img.get_width() * scale)
                h = int(img.get_height() * scale)
                img = pygame.transform.scale(img, (w, h))
            frames.append(img)

        return frames

    def clear_cache(self) -> None:
        """清空缓存（切换场景时调用）。"""
        self._cache.clear()


# ── 模块级快捷函数 ──────────────────────────────────

_loader = SpriteLoader()


def load_image(path: str) -> pygame.Surface:
    return _loader.load_image(path)


def load_frames(directory: str, prefix: str = "", scale: float = 1.0) -> list[pygame.Surface]:
    return _loader.load_frames(directory, prefix, scale)
