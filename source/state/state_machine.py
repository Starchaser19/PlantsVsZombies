"""栈式状态机 — 管理游戏状态的切换与生命周期。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import pygame


class GameState(ABC):
    """游戏状态抽象基类。

    每个具体状态（菜单、游戏内、暂停……）实现这一接口。
    """

    def __init__(self, machine: "StateMachine") -> None:
        self.machine = machine

    @abstractmethod
    def enter(self, *args, **kwargs) -> None:
        """状态被推入栈顶时调用。"""

    @abstractmethod
    def exit(self) -> None:
        """状态被弹出时调用（用于清理）。"""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """处理输入事件。"""

    @abstractmethod
    def update(self, dt: float) -> None:
        """逻辑更新。

        Args:
            dt: 距离上一帧的秒数（delta time）。
        """

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """渲染到屏幕。"""


class StateMachine:
    """栈式状态机。

    - ``push(state)`` 暂停当前状态，进入新状态
    - ``pop()`` 退出当前状态，恢复上一状态
    - ``change(state)`` 替换当前状态（pop + push 的快捷方式）
    """

    def __init__(self) -> None:
        self._stack: list[GameState] = []

    # ── 属性 ──────────────────────────────────────────

    @property
    def current(self) -> Optional[GameState]:
        """当前栈顶状态。"""
        return self._stack[-1] if self._stack else None

    @property
    def is_empty(self) -> bool:
        return len(self._stack) == 0

    # ── 操作 ──────────────────────────────────────────

    def push(self, state: GameState, *args, **kwargs) -> None:
        """暂停当前状态（若存在），将新状态压入栈顶。"""
        if self.current is not None:
            self.current.exit()
        self._stack.append(state)
        state.enter(*args, **kwargs)

    def pop(self) -> Optional[GameState]:
        """弹出栈顶状态并恢复下一状态。"""
        if not self._stack:
            return None
        removed = self._stack.pop()
        removed.exit()
        # 恢复下层状态
        if self.current is not None:
            self.current.enter()
        return removed

    def change(self, state: GameState, *args, **kwargs) -> None:
        """用新状态替换栈顶状态。"""
        if self._stack:
            self._stack.pop().exit()
        self.push(state, *args, **kwargs)

    def clear(self) -> None:
        """清空所有状态。"""
        while self._stack:
            self._stack.pop().exit()
