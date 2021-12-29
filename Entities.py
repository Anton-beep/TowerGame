import pygame

from start import SPRITES_GROUPS, CONFIG
from Players import Player
from Sprites import load_images, load_image
from itertools import cycle
from random import randint
from math import copysign, sqrt


class Entity(pygame.sprite.Sprite):
    def __init__(self, player, hp, max_hp, group=None):
        if group is not None:
            super().__init__(group)
        else:
            super().__init__()
        self.hp = hp
        self.max_hp = max_hp
        self.player = player

    def get_hp(self, hp_get: int):
        """Increases hp for entity, if self.hp + hp_get > self.max_hp then self.hp = self.max_hp"""
        self.hp = min(self.max_hp, hp_get)

    def get_damage(self, entity, damage: int) -> bool:
        """Decreases hp for entity, if self.hp - damage <= 0 then returns True, which means dead"""
        self.hp -= damage
        if self.hp <= 0:
            self.kill()
            return True
        return False

    def update(self):
        pass


class Moving_entity(Entity):
    def __init__(self, moving_images: cycle, player: Player, hp, max_hp, group=None):
        super().__init__(player, hp, max_hp, group)

        self.moving_images = moving_images

        self.image = next(moving_images)
        self.target = None

        self.looking_at = 1
        # looking positions: 3 - top, 0 - right, 1 - bottom, 2 - left

    def set_target(self, new):
        self.target = new

    def move(self, motion, draw=True):
        self.rect = self.rect.move(motion)
        for group in SPRITES_GROUPS.values():
            if not pygame.sprite.spritecollide(self, group, False) in [[], [self]]:
                self.rect = self.rect.move(*tuple(map(lambda x: -x, motion)))
                return False
        if not draw:
            self.rect = self.rect.move(*tuple(map(lambda x: -x, motion)))
        else:
            if abs(motion[0]) > abs(motion[1]):
                if motion[0] > 0:
                    self.looking_at = 0
                else:
                    self.looking_at = 2
            else:
                if motion[1] > 0:
                    self.looking_at = 3
                else:
                    self.looking_at = 1
        return True

    def get_motion_for_bypass(self, coords1, coords2):
        flag = True
        while flag:

            if ((self.rect.center[0] - coords1[0]) / (coords2[0] - coords1[0])
                    == (self.rect.center[1] - coords1[1]) / (coords2[1] - coords1[1])):
                flag = False

    def move_to_target(self):
        """moves self to target
        :returns True if moved else False"""

        if type(self.target) != tuple:
            coords = self.target.rect.center
        else:
            coords = self.target

        delta_x = coords[0] - self.rect.center[0]
        delta_y = coords[1] - self.rect.center[1]
        print(delta_x, delta_y)
        if delta_x == 0 and delta_y == 0:
            return False
        if delta_x == 0:
            if self.move((copysign(1, delta_x), 0)):
                self.image = pygame.transform.rotate(next(self.moving_images), self.looking_at * 90)
                return True
        elif delta_y == 0:
            if self.move((0, copysign(1, delta_y))):
                self.image = pygame.transform.rotate(next(self.moving_images), self.looking_at * 90)
                return True
        elif self.move((round(copysign(abs(delta_x / (abs(delta_x) + abs(delta_y))), delta_x)),
                        round(copysign(abs(delta_y / (abs(delta_x) + abs(delta_y))), delta_y)))):
            self.image = pygame.transform.rotate(next(self.moving_images), self.looking_at * 90)
            return True
        return False


class Warriors(Moving_entity):
    def __init__(self, spawn_coords: tuple, player: Player, add_to_group=True):
        if add_to_group:
            super().__init__(cycle(load_images(CONFIG['warriors']['Moving_images'])),
                             player,
                             CONFIG.getint('warriors', 'HP'),
                             CONFIG.getint('warriors', 'HPMax'), SPRITES_GROUPS['ENTITIES'])
        else:
            super().__init__(cycle(load_images(CONFIG['warriors']['Moving_images'])),
                             player,
                             CONFIG.getint('warriors', 'HP'),
                             CONFIG.getint('warriors', 'HPMax'))

        self.attack_images = cycle(load_images(CONFIG['warriors']['Attacking_images']))
        self.standing_image = cycle(load_images(CONFIG['warriors']['Standing_images']))

        self.image = next(self.standing_image)
        self.rect = self.image.get_rect()
        self.rect.center = spawn_coords

        self.player = player
        self.target = None
        self.strength = CONFIG.getint('warriors', 'Strength')
        self.distance_to_attack = CONFIG.getint('warriors', 'DistanceToAttack')

    def get_damage(self, entity: Entity, damage: int) -> bool:
        """Gets some damage and if self.target is None then self.target is Entity
        from which the damage was taken"""
        if self.target is None:
            self.target = entity
        return super().get_damage(entity, damage)

    def attack_target(self):
        """attack target and animation"""
        self.image = next(self.attack_images)

        return self.target.get_damage(self, self.strength + randint(-5, 5))

    def update(self):
        """moves self to target or attack target, check attacking with collide"""
        # can use next(<itertools.cycle>) for animation (check itertools.cycle)
        if self.target is None or (type(self.target) != tuple and self.target.hp <= 0):
            self.target = None
        if self.target is not None:
            if not self.move_to_target():
                if type(self.target) != tuple:
                    target_coords = self.target.rect.center
                else:
                    target_coords = self.target
                dist = sqrt(abs(self.rect.center[0] - target_coords[0]) ** 2 +
                            abs(self.rect.center[1] - target_coords[1]) ** 2)
                if type(self.target) == tuple and dist <= 1:
                    self.target = None
                elif type(self.target) != tuple \
                        and dist <= self.distance_to_attack + self.target.rect.width:
                    if self.attack_target():
                        self.target = None
                    return None
                else:
                    self.image = next(self.standing_image)
        else:
            self.image = next(self.standing_image)
        print(self.target)


class Tower(Entity):
    def __init__(self, spawn_coords: tuple, player: Player, add_to_group=True):
        if add_to_group:
            super().__init__(player, CONFIG.getint('tower', 'HP'),
                             CONFIG.getint('tower', 'HPMax'), SPRITES_GROUPS['ENTITIES'])
        else:
            super().__init__(player, CONFIG.getint('tower', 'HP'),
                             CONFIG.getint('tower', 'HPMax'))
        self.standing_image = load_image('data/tower/standing.png')

        self.image = self.standing_image
        self.rect = self.image.get_rect()
        self.rect.center = spawn_coords

        self.player = player

# Warriors(Player('red')).get_damage(Warriors(Player('blue')), 100)
