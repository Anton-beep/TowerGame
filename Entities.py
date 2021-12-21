import pygame

from main import SPRITES_GROUPS, CONFIG
from Players import Player


class Entity(pygame.sprite.Sprite):
    def __init__(self, group, hp, max_hp):
        super().__init__(group)
        self.hp = hp
        self.max_hp = max_hp

    def get_hp(self, hp_get: int):
        """Increases hp for entity, if self.hp + hp_get > self.max_hp then self.hp = self.max_hp"""
        self.hp = min(self.max_hp, hp_get)

    def get_damage(self, damage: int) -> bool:
        """Decreases hp for entity, if self.hp - damage <= 0 then returns True, which means dead"""
        self.hp -= damage
        return True if self.hp <= 0 else False


class Warriors(Entity):
    def __init__(self, player: Player):
        super().__init__(SPRITES_GROUPS['ENTITIES'], CONFIG['WarriorsHP'])