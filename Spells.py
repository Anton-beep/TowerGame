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
        self.start_time = None
        self.rect = self.icon.get_rect()
        self.rect.center = (300, 300)
        self.status = True
        self.recharge_time = CONFIG.getint('lightning', 'recharge')

    def select_spell(self, choose):
        if choose and self.status is True:
            icon = load_image(CONFIG['lightning']['Icon_images'])
            self.image = icon
        elif self.status is True:
            icon = load_image(CONFIG['lightning']['Active_icon'])
            self.image = icon
            return 1

    def damage_light(self, timing):
        self.start_time = timing
        icon = load_image(CONFIG['lightning']['Disable_icon'])
        self.image = icon
        self.status = False
        return self.damage

    def return_status(self):
        return self.status

    def update(self, now_time):
        if self.start_time is not None and now_time - self.start_time >= self.recharge_time:
            self.start_time = None
            icon = load_image(CONFIG['lightning']['Icon_images'])
            self.image = icon
            self.status = True
