"""字体加载辅助 — 统一使用嵌入的中文字体，避免系统字体兼容问题。"""

from __future__ import annotations

from pathlib import Path

import pygame

_FONTS_DIR = Path(__file__).parent.parent.parent / "resources" / "fonts"


def get_font(size: int, *, bold: bool = False) -> pygame.font.Font:
    """获取中文字体。

    优先使用嵌入的 simhei.ttf，不存在时回退到 Pygame 默认字体。
    """
    font_path = _FONTS_DIR / "simhei.ttf"
    if font_path.exists():
        font = pygame.font.Font(str(font_path), size)
    else:
        font = pygame.font.Font(None, size)
    font.set_bold(bold)
    return font
