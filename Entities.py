import pygame

from start import SPRITES_GROUPS, CONFIG
from Players import Player
from Sprites import load_images, load_image
from itertools import cycle


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

    def update(self):
        pass


class Warriors(Entity):
    def __init__(self, spawn_coords: tuple, player: Player, add_to_group=True):
        if add_to_group:
            super().__init__(CONFIG.getint('warriors', 'HP'),
                             CONFIG.getint('warriors', 'HPMax'), SPRITES_GROUPS['ENTITIES'])
        else:
            super().__init__(CONFIG.getint('warriors', 'HP'),
                             CONFIG.getint('warriors', 'HPMax'))
        self.moving_images = cycle(load_images(CONFIG['warriors']['Moving_images']))
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
            self.target = Entity
        return super().get_damage(entity, damage)

    def move_to_target(self, speed):
        """moves self to target"""
        if type(self.target) == Entity:
            pass
        elif type(self.target) == tuple:
            pass

    def attack_target(self):
        """attack target and animation"""
        self.target.get_damage(self, self.strength)

    def set_target(self, target):
        self.target = target

    def update(self):
        """moves self to target or attack target, check attacking with collide"""
        # can use next(<itertools.cycle>) for animation (check itertools.cycle)
        pass


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

    def update(self):
        self.image = next(self.standing_image)


# Warriors(Player('red')).get_damage(Warriors(Player('blue')), 100)
