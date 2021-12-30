import pygame
import time
import sys
import os

from start import SPRITES_GROUPS, CONFIG
from main import *
from Sprites import load_image


class spell_circle(pygame.sprite.Sprite):
    def __init__(self, radius, coordinates: tuple, color, *group):
        super().__init__(*group)
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        self.color = color
        self.rect = pygame.Rect(coordinates[0], coordinates[1], 2 * radius, 2 * radius)
        self.rect.center = coordinates

    def draw(self):
        pygame.draw.circle(self.image, pygame.Color(self.color),
                           (self.radius, self.radius), self.radius)


class Spell(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.status = True
        self.start_time = None

    def return_status(self):
        return self.status


class Lightning_spell(Spell):
    icon = load_image(CONFIG['lightning']['Icon_images'])

    def __init__(self, *group):
        super().__init__(*group)
        self.damage = CONFIG.getint('lightning', 'damage')
        self.recharge_time = CONFIG.getint('lightning', 'recharge')

        self.image = Lightning_spell.icon
        self.rect = self.icon.get_rect()
        self.rect.center = (300, 300)

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

    def update(self, now_time):
        if self.start_time is not None and now_time - self.start_time >= self.recharge_time:
            self.start_time = None
            icon = load_image(CONFIG['lightning']['Icon_images'])
            self.image = icon
            self.status = True


class Poison_spell(Spell):
    icon = load_image(CONFIG['poison']['Icon_image'])

    def __init__(self, *group):
        super().__init__(*group)
        self.damage = CONFIG.getint('poison', 'damage')
        self.radius = CONFIG.getint('poison', 'radius')
        self.recharge_time = CONFIG.getint('poison', 'recharge')

        self.range_of_poison = []
        self.image = Poison_spell.icon
        self.rect = self.icon.get_rect()
        self.rect.center = (200, 300)

    def select_spell(self, choose):
        if choose and self.status is True:
            icon = load_image(CONFIG['poison']['Icon_images'])
            self.image = icon
        elif self.status is True:
            icon = load_image(CONFIG['poison']['Active_icon'])
            self.image = icon
            return 2

    def damage_poison(self, timing, coordinates):
        self.start_time = timing
        icon = load_image(CONFIG['poison']['Disable_icon'])
        self.image = icon
        self.range_of_poison.append(spell_circle(self.radius, coordinates, 'green', SPRITES_GROUPS['POISON_CIRCLE']))
        self.status = False

    def update(self, now_time):
        if self.start_time is not None and now_time - self.start_time >= self.recharge_time:
            self.start_time = None
            icon = load_image(CONFIG['poison']['Icon_images'])
            self.image = icon
            self.status = True
        else:
            for i in self.range_of_poison:
                i.draw()
