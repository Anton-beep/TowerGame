import pygame

from start import SPRITES_GROUPS, CONFIG
from Players import Player
from Sprites import load_images, load_image
from itertools import cycle
from random import randint
from math import copysign


class Entity(pygame.sprite.Sprite):
    def __init__(self, hp, max_hp, group=None):
        if group is not None:
            super().__init__(group)
        else:
            super().__init__()
        self.hp = hp
        self.max_hp = max_hp

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
        super().__init__(hp, max_hp, group)

        self.player = player
        self.moving_images = moving_images

        self.image = next(moving_images)
        self.target = None

    def set_target(self, new):
        self.target = new

    def move_to_target(self):
        """moves self to target
        :returns True if moved else False"""
        self.image = next(self.moving_images)

        coords = self.target.rect.center
        delta_x = self.rect.center[0] - coords[0]
        delta_y = self.rect.center[1] - coords[1]
        if delta_x == 0 and delta_y == 0:
            return False
        if delta_y != 0 and abs(delta_x / delta_y) > 1:
            delta = (copysign(1, -delta_x), 0)
        else:
            delta = (0, copysign(1, -delta_y))
        self.rect = self.rect.move(delta)
        for group in SPRITES_GROUPS.values():
            if not pygame.sprite.spritecollide(self, group, False) in [[], [self]]:
                self.rect = self.rect.move(*tuple(map(lambda x: -x, delta)))
                return False
        return True


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
        if self.target.hp <= 0:
            self.target = None
        if self.target is not None:
            if not self.move_to_target():
                if self.attack_target():
                    self.target = None
        else:
            self.image = next(self.standing_image)


class Tower(Entity):
    def __init__(self, spawn_coords: tuple, player: Player, add_to_group=True):
        if add_to_group:
            super().__init__(CONFIG.getint('tower', 'HP'),
                             CONFIG.getint('tower', 'HPMax'), SPRITES_GROUPS['ENTITIES'])
        else:
            super().__init__(CONFIG.getint('tower', 'HP'),
                             CONFIG.getint('tower', 'HPMax'))
        self.standing_image = load_image('data/tower/standing.png')

        self.image = self.standing_image
        self.rect = self.image.get_rect()
        self.rect.center = spawn_coords

        self.player = player

# Warriors(Player('red')).get_damage(Warriors(Player('blue')), 100)
