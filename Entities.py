import pygame
from start import *
from boards import Cell, Board
from Sprites import *
from itertools import cycle
from Players import Player
from math import copysign


class Entity(pygame.sprite.Sprite):
    def __init__(self, player, hp, max_hp, board: Board, group=None):
        if group is not None:
            super().__init__(group)
        else:
            super().__init__()
        self.hp = hp
        self.max_hp = max_hp
        self.player = player
        self.board = board

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

    def get_int(self):
        return 0

    def get_intersection(self, other, dist) -> bool:
        """Checks if other.rect intersects with self.rect at the dist"""
        return get_intersection_two_rects(self.rect, other.rect, dist)


class Moving_entity(Entity):
    def __init__(self, moving_images: cycle, player: Player, hp, max_hp, board, group=None):
        super().__init__(player, hp, max_hp, board, group)

        self.moving_images = moving_images

        self.image = next(moving_images)
        self.target = None
        self.checkpoint = None

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

    def move_to_target(self):
        if self.target is None:
            return False

        if self.checkpoint is None:
            # need to create road for entity
            if type(self.target) == tuple:
                coords = self.target
            else:
                coords = self.target.rect.center

            self.checkpoint = self.board.road_to_coords(
                tuple(map(lambda x: x // self.board.cell_size, self.rect.center)),
                tuple(map(lambda x: x // self.board.cell_size, coords)))[::-1][1]
        else:
            # go and check collide
            delta_x = self.checkpoint[0] * self.board.cell_size - self.rect.center[0]
            delta_y = self.checkpoint[1] * self.board.cell_size - self.rect.center[1]
            if delta_y != 0:
                self.move((0, copysign(1, delta_y)))
            else:
                self.move((copysign(1, delta_x), 0))
            print(list(map(lambda x: x // self.board.cell_size, self.rect.center)))
            if list(map(lambda x: x // self.board.cell_size, self.rect.center)) == self.checkpoint:
                self.checkpoint = None


class Warriors(Moving_entity):
    def __init__(self, spawn_coords: tuple, player: Player, board: Board, add_to_group=True):
        if add_to_group:
            super().__init__(cycle(load_images(CONFIG['warriors']['Moving_images'])), player,
                             CONFIG.getint('warriors', 'HP'),
                             CONFIG.getint('warriors', 'HPMax'),
                             board,
                             SPRITES_GROUPS['ENTITIES'])
        else:
            super().__init__(cycle(load_images(CONFIG['warriors']['Moving_images'])), player,
                             CONFIG.getint('warriors', 'HP'),
                             CONFIG.getint('warriors', 'HPMax'),
                             board)

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

        return self.target.get_damage(self, self.strength)

    def update(self):
        self.move_to_target()


class Tower(Entity):
    def __init__(self, spawn_coords: tuple, player: Player, board: Board, add_to_group=True):
        if add_to_group:
            super().__init__(player, CONFIG.getint('tower', 'HP'),
                             CONFIG.getint('tower', 'HPMax'), board, SPRITES_GROUPS['ENTITIES'])
        else:
            super().__init__(player, CONFIG.getint('tower', 'HP'),
                             CONFIG.getint('tower', 'HPMax'), board)
        self.standing_image = load_image('data/tower/standing.png')

        self.image = self.standing_image
        self.rect = self.image.get_rect()
        self.rect.center = spawn_coords

        self.player = player
