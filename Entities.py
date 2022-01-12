import time

import numpy as np
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
        return -1

    def get_intersection(self, other, dist) -> bool:
        """Checks if other.rect intersects with self.rect at the dist"""
        return get_intersection_two_rects(self.rect, other.rect, dist)

    def click(self, coords) -> bool:
        return self.rect.collidepoint(coords)


class Moving_entity(Entity):
    def __init__(self, moving_images: cycle, player: Player, hp, max_hp, board, group=None):
        super().__init__(player, hp, max_hp, board, group)

        self.moving_images = moving_images

        self.image = next(moving_images)
        self.target = None
        self.checkpoint = None

        self.looking_at = 1
        self.road = None
        self.update_road_int = 50
        self.update_road_iter = self.update_road_int
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
            self.image = pygame.transform.rotate(next(self.moving_images), self.looking_at * 90)
        return True

    def set_new_road(self):
        args_for_board = [self]
        if type(self.target) == tuple:
            coords = self.target
        else:
            coords = self.target.rect.center
            args_for_board.append(self.target)

        self.road = self.board.road_to_coords(
            tuple(map(lambda x: x // self.board.cell_size, self.rect.center)),
            tuple(map(lambda x: x // self.board.cell_size, coords)),
            *args_for_board
        )

    def set_new_checkpoint(self):
        # need to create road for entity
        self.checkpoint = None
        if self.road is None or len(self.road) < 2:
            if self.update_road_iter >= self.update_road_int:
                self.set_new_road()
                self.update_road_iter = 0
            if self.update_road_iter < self.update_road_int:
                self.update_road_iter += 1
        if self.road is not None:
            try:
                self.checkpoint = list(map(lambda x: x * self.board.cell_size, self.road[-2]))
                del self.road[-2]
            except IndexError:
                pass
            except TypeError:
                pass

            self.move_to_target()

    def move_to_target(self):
        if self.update_road_iter < self.update_road_int:
            self.update_road_iter += 1

        if self.target is None:
            return False

        if self.checkpoint is None:
            self.set_new_checkpoint()

            if type(self.target) == tuple and list(map(lambda x: x // self.board.cell_size, self.rect.center)) ==\
                    list(map(lambda x: x // self.board.cell_size, self.target)):
                self.checkpoint = self.target
        else:
            # go and check collide
            delta_x = self.checkpoint[0] - self.rect.center[0]
            delta_y = self.checkpoint[1] - self.rect.center[1]

            flag = False
            if delta_x == 0 and delta_y != 0:
                flag = self.move((0, copysign(1, delta_y)))
            elif delta_y == 0 and delta_x != 0:
                flag = self.move((copysign(1, delta_x), 0))
            elif delta_x != 0 and delta_y != 0:
                flag = self.move((copysign(1, delta_x), 0))

            if abs(delta_x) <= 1 and abs(delta_y) <= 1:
                self.set_new_checkpoint()
            return flag


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
        self.speed = CONFIG.getint('warriors', 'Speed')
        self.speed_cooldown = cycle(range(self.speed + 1))
        self.attack_speed = CONFIG.getint('warriors', 'CoolDownAttack')
        self.attack_cooldown = cycle(range(self.attack_speed + 1))
        self.distance_to_attack = CONFIG.getint('warriors', 'DistanceToAttack')
        self.cost = CONFIG.getint('warriors', 'Cost')

    def get_damage(self, entity: Entity, damage: int) -> bool:
        """Gets some damage and if self.target is None then self.target is Entity
        from which the damage was taken"""
        if self.target is None:
            self.target = entity
        return super().get_damage(entity, damage)

    def attack_target(self):
        """attack target and animation"""
        if next(self.attack_cooldown) == self.attack_speed:
            self.image = pygame.transform.rotate(next(self.attack_images), self.looking_at * 90)

            return self.target.get_damage(self, self.strength)
        return False

    def move_to_target(self):
        if next(self.speed_cooldown) == self.speed:
            return super().move_to_target()
        return False

    def update(self):
        if self.target is not None:
            if type(self.target) != tuple:
                if self.target.hp <= 0:
                    self.target = None
                    return None
            if type(self.target) == tuple:
                self.move_to_target()
                if self.rect.center == self.target:
                    self.target = None
            else:
                if self.get_intersection(self.target, self.distance_to_attack):
                    if self.attack_target():
                        self.target = None
                else:
                    self.move_to_target()
        else:
            self.image = pygame.transform.rotate(next(self.standing_image), self.looking_at * 90)


class Tower(Entity):
    def __init__(self, spawn_coords: tuple, player: Player, board: Board, add_to_group=True):
        self.standing_image = load_image('data/tower/standing.png')
        self.image = self.standing_image
        self.rect = self.image.get_rect()
        self.rect.center = spawn_coords

        self.player = player

        self.money = CONFIG.getint('player', 'MoneyStart')
        self.money_max = CONFIG.getint('player', 'MoneyMax')

        if add_to_group:
            super().__init__(player, CONFIG.getint('tower', 'HP'),
                             CONFIG.getint('tower', 'HPMax'), board, SPRITES_GROUPS['ENTITIES'])
        else:
            super().__init__(player, CONFIG.getint('tower', 'HP'),
                             CONFIG.getint('tower', 'HPMax'), board)
