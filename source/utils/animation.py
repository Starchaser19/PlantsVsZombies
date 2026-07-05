"""帧动画控制器。"""

from __future__ import annotations

import pygame


class Animation:
    """单组帧动画。

    循环播放一组帧，按 frame_duration 秒每帧的速度切换。
    """

    def __init__(
        self,
        frames: list[pygame.Surface],
        frame_duration: float = 0.1,
        *,
        loop: bool = True,
    ) -> None:
        if not frames:
            raise ValueError("frames 不能为空")
        self._frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self._timer = 0.0
        self._index = 0
        self._finished = False

    @property
    def current_frame(self) -> pygame.Surface:
        return self._frames[self._index]

    @property
    def finished(self) -> bool:
        """非循环动画是否已播放完毕。"""
        return self._finished

    def update(self, dt: float) -> None:
        if self._finished:
            return
        self._timer += dt
        if self._timer >= self.frame_duration:
            self._timer -= self.frame_duration
            self._index += 1
            if self._index >= len(self._frames):
                if self.loop:
                    self._index = 0
                else:
                    self._index = len(self._frames) - 1
                    self._finished = True

    def reset(self) -> None:
        self._timer = 0.0
        self._index = 0
        self._finished = False


class Animator:
    """多状态动画管理器。

    管理实体在不同状态（walk/attack/die/idle）下的动画切换。
    """

    def __init__(self, animations: dict[str, Animation], initial_state: str = "idle") -> None:
        self._animations = animations
        self._current_state = initial_state

    @property
    def current_state(self) -> str:
        return self._current_state

    @property
    def current_frame(self) -> pygame.Surface:
        anim = self._animations.get(self._current_state)
        if anim is None:
            # 回退到第一个可用动画
            anim = next(iter(self._animations.values()))
        return anim.current_frame

    def set_state(self, state: str) -> None:
        """切换状态。同状态重复调用无副作用。"""
        if state == self._current_state:
            return
        if state in self._animations:
            self._animations[state].reset()
            self._current_state = state

    def update(self, dt: float) -> None:
        anim = self._animations.get(self._current_state)
        if anim:
            anim.update(dt)

    def add_animation(self, state: str, animation: Animation) -> None:
        self._animations[state] = animation
