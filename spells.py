import pygame
import time
import sys
import os

from pygame.sprite import Sprite

from start import SPRITES_GROUPS, CONFIG
from main import *
from entities import *


class spell_circle(pygame.sprite.Sprite):
    def __init__(self, radius, coordinates: tuple, color, timing, tick, start_time,
                 rectFit, *group):
        super().__init__(*group)
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        self.time = timing
        self.tick = tick
        self.start_time = start_time
        self.time_tick = start_time
        self.attack_time = start_time

        self.color = color
        self.rect = pygame.Rect(coordinates[0], coordinates[1], 2 * radius, 2 * radius)
        self.rect.center = coordinates

        self.image.set_clip(rectFit.move(-coordinates[0] + radius,
                                         -coordinates[1] + radius))

    def draw(self, hp, key):
        if time.time() - self.start_time >= self.time:
            self.kill()
            for spell in SPRITES_GROUPS['SPELLS']:
                if key == 'damage':
                    try:
                        spell.range_of_poison.remove(self)
                    except AttributeError:
                        pass
                elif key == 'heal':
                    try:
                        spell.range_of_heal.remove(self)
                    except AttributeError:
                        pass

        if time.time() - self.time_tick >= self.tick:
            for entity in pygame.sprite.spritecollide(self, SPRITES_GROUPS['ENTITIES'], False):
                if entity.player == BOT_ENEMY:
                    if key == 'damage':
                        entity.get_damage(Entity, hp,
                                          'Заклинание яд',
                                          PLAYER.getRussianName())
                if entity.player == PLAYER:
                    if key == 'heal':
                        entity.get_hp(hp + entity.hp)
                self.time_tick = time.time()
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
        self.cost = CONFIG.getint('lightning', 'cost')

        self.image = Lightning_spell.icon
        self.rect = self.icon.get_rect()
        self.rect.center = (500, 600)

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
        self.cost = CONFIG.getint('poison', 'cost')

        self.poison_time = CONFIG.getint('poison', 'poison_time')
        self.damage_tick = CONFIG.getint('poison', 'damage_tick')

        self.range_of_poison = []

        self.image = Poison_spell.icon
        self.rect = self.icon.get_rect()
        self.rect.center = (300, 600)

    def select_spell(self, choose):
        if choose and self.status is True:
            icon = load_image(CONFIG['poison']['Icon_image'])
            self.image = icon
        elif self.status is True:
            icon = load_image(CONFIG['poison']['Active_icon'])
            self.image = icon
            return 2

    def damage_poison(self, timing, coordinates, rectFit):
        self.start_time = timing
        icon = load_image(CONFIG['poison']['Disable_icon'])
        self.image = icon
        print(rectFit)
        self.range_of_poison.append(
            spell_circle(self.radius, coordinates, (0, 255, 0, 175), self.poison_time, self.damage_tick,
                         self.start_time, rectFit,
                         CIRCLE_SPRITES_GROUPS['POISON_CIRCLE']))
        self.status = False

    def update(self, now_time):
        if self.start_time is not None and now_time - self.start_time >= self.recharge_time:
            self.start_time = None
            icon = load_image(CONFIG['poison']['Icon_image'])
            self.image = icon
            self.status = True
        else:
            for i in self.range_of_poison:
                i.draw(self.damage, 'damage')


class Heal_spell(Spell):
    icon = load_image(CONFIG['heal']['Icon_image'])

    def __init__(self, *group):
        super().__init__(*group)
        self.heal = CONFIG.getint('heal', 'heal')
        self.radius = CONFIG.getint('heal', 'radius')
        self.recharge_time = CONFIG.getint('heal', 'recharge')
        self.cost = CONFIG.getint('heal', 'cost')

        self.heal_time = CONFIG.getint('heal', 'heal_time')
        self.heal_tick = CONFIG.getint('heal', 'heal_tick')

        self.range_of_heal = []

        self.image = Heal_spell.icon
        self.rect = self.icon.get_rect()
        self.rect.center = (100, 600)

    def select_spell(self, choose):
        if choose and self.status is True:
            icon = load_image(CONFIG['heal']['Icon_image'])
            self.image = icon
        elif self.status is True:
            icon = load_image(CONFIG['heal']['Active_icon'])
            self.image = icon
            return 3

    def damage_poison(self, timing, coordinates, rectFit):
        self.start_time = timing
        icon = load_image(CONFIG['heal']['Disable_icon'])
        self.image = icon
        self.start_time1 = timing
        self.range_of_heal.append(
            spell_circle(self.radius, coordinates, (255, 255, 0, 175), self.heal_time, self.heal_tick,
                         self.start_time, rectFit,
                         CIRCLE_SPRITES_GROUPS['HEAL_CIRCLE']))
        self.status = False

    def update(self, now_time):
        if self.start_time is not None and now_time - self.start_time >= self.recharge_time:
            self.start_time = None
            icon = load_image(CONFIG['heal']['Icon_image'])
            self.image = icon
            self.status = True
        else:
            for i in self.range_of_heal:
                i.draw(self.heal, 'heal')
