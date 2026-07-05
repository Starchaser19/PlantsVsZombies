"""卡片面板 — 顶部木条上的植物卡片栏。"""

from __future__ import annotations

import pygame

from source.ui.card import Card

ALL_CARDS: dict[str, tuple[int, float, str]] = {
    "sunflower":  (50,  7.5,  "向日葵"),
    "peashooter": (100, 7.5,  "豌豆"),
    "wallnut":    (50,  30.0, "坚果"),
    "cherrybomb": (150, 50.0, "樱桃"),
    "potatomine": (25,  30.0, "土豆雷"),
    "snowpea":    (175, 7.5,  "寒冰"),
    "repeater":   (200, 7.5,  "双发"),
}


class CardPanel:
    """顶部木条上的植物卡片栏。"""

    PADDING = 4
    # 卡片纵向居中在 92px 高的木条上
    Y_OFFSET = (92 - Card.HEIGHT) // 2
    # 阳光数占位宽度，卡片从此之后开始
    START_X = 110

    def __init__(self, card_types: list[str] | None = None) -> None:
        self.cards: list[Card] = []
        self.rects: dict[str, pygame.Rect] = {}

        if card_types is None:
            card_types = ["sunflower", "peashooter"]

        x = self.START_X
        for plant_type in card_types:
            if plant_type in ALL_CARDS:
                cost, cd, label = ALL_CARDS[plant_type]
                card = Card(plant_type, cost, cd, label)
                card.set_position(x, self.Y_OFFSET)
                x += Card.WIDTH + self.PADDING
                self.cards.append(card)
                self.rects[plant_type] = card.rect

    def update(self, dt: float) -> None:
        for card in self.cards:
            card.update(dt)

    def draw(self, screen: pygame.Surface, sun_value: int) -> None:
        for card in self.cards:
            card.draw(screen, can_afford=(sun_value >= card.sun_cost))

    def get_clicked(self, pos: tuple[int, int]) -> str | None:
        for card in self.cards:
            if card.rect.collidepoint(pos):
                return card.plant_type
        return None

    def get_card(self, plant_type: str) -> Card | None:
        for card in self.cards:
            if card.plant_type == plant_type:
                return card
        return None
