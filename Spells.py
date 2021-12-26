import pygame
import time
import sys
import os

from start import SPRITES_GROUPS, CONFIG
from main import *
from Sprites import load_image


class Lightning_spell(pygame.sprite.Sprite):
    icon = load_image(CONFIG['lightning']['Icon_images'])

    def __init__(self, *group):
        super().__init__(*group)
        self.damage = CONFIG.getint('lightning', 'Damage')
        self.image = Lightning_spell.icon

        self.rect = self.icon.get_rect()
        self.rect.center = (300, 300)

    def select_spell(self, choose):
        if choose:
            icon = load_image(CONFIG['lightning']['Icon_images'])
            self.image = icon
        else:
            icon = load_image(CONFIG['lightning']['Active_icon'])
            self.image = icon

    def damage(self, position):
        return self.damage
