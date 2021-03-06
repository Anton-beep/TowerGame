"""entities"""

from itertools import cycle
from math import copysign
from random import randint
from datetime import datetime as dt

import pygame
from start import *
from boards import Cell, Board
from sprites import *
from players import Player
from buttons import Button, PushButton


class Entity(pygame.sprite.Sprite):
    """standard entity"""

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

    def get_damage(self, entity, damage: int, self_entity_name, entity_name=None,
                   attack_player=None) -> bool:
        """Decreases hp for entity, if self.hp - damage <= 0 then returns True, which means dead"""
        self.hp -= damage + randint(round(-damage * 0.2), round(damage * 0.2))
        if self.hp <= 0:
            self.kill()
            print()
            if attack_player is None:
                attack_player = entity.player.getRussianName()
            if entity_name is None:
                entity_name = type(entity).getRussianName()

            if entity_name == 'Игрок':
                RES_FILE.write(f'[{str(dt.now())}] : {attack_player} убил {self_entity_name} '
                               f'игрока '
                               f'{self.player.getRussianName()}\n')
            else:
                RES_FILE.write(f'[{str(dt.now())}] : {attack_player} убил {self_entity_name} '
                               f'при помощи {entity_name}\n')
            return True
        return False

    def get_int(self):
        """int for board (not used)"""
        return -1

    def get_intersection(self, other, dist) -> bool:
        """Checks if other.rect intersects with self.rect at the dist"""
        return get_intersection_two_rects(self.rect, other.rect, dist)

    def click(self, coords) -> bool:
        """check if coords of point collides self"""
        return self.rect.collidepoint(coords)


class MovingEntity(Entity):
    """Standard Entity, but can move"""

    def __init__(self, moving_images: cycle, player: Player, hp, max_hp, board, group=None):
        super().__init__(player, hp, max_hp, board, group)

        self.moving_images = moving_images

        self.image = next(moving_images)
        self.image_raw = self.image
        self.targets = [None]
        self.target_now = None
        self.checkpoint = None
        self.rect = None

        self.moving_img_Int = 5
        self.moving_img_cooldown = cycle(range(self.moving_img_Int + 1, 0, -1))
        self.looking_at = 1
        self.road = None
        self.update_road_int = 50
        self.update_road_iter = self.update_road_int
        # looking positions: 3 - top, 0 - right, 1 - bottom, 2 - left

    def set_target(self, new):
        """sets new target for entity and deletes old targets"""
        self.targets = [None, new]
        self.road = None
        self.checkpoint = None
        self.target_now = self.targets[-1]

    def set_targets(self, new):
        """sets new targets for entity and deletes old targets"""
        self.targets = [None] + new[::-1]
        self.road = None
        self.checkpoint = None
        self.target_now = self.targets[-1]

    def move(self, motion, draw=True):
        """try to move self.rect with motion and controls looking_at"""
        self.rect = self.rect.move(motion)
        for group in SPRITES_GROUPS.values():
            list_collide = pygame.sprite.spritecollide(self, group, False)
            list_collide = list(filter(lambda x: not isinstance(x, PushButton), list_collide))
            if list_collide not in [[], [self]]:
                self.rect = self.rect.move(*tuple(map(lambda x: -x, motion)))
                # print(list(filter(lambda x: x.player != self.player, list_collide)))
                filter_list = filter(lambda x: str(type(x))[:17].lower() == "<class 'entities."
                                               and x.player != self.player
                                               and x.hp > 0, list_collide)
                self.targets.extend(list(filter_list))
                self.target_now = self.targets[-1]
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
            if next(self.moving_img_cooldown) == self.moving_img_Int:
                self.image_raw = next(self.moving_images)
            self.image = pygame.transform.rotate(self.image_raw, self.looking_at * 90)
        return True

    def set_new_road(self):
        """sets new road to target, using board"""
        args_for_board = [self]
        if isinstance(self.target_now, tuple):
            coords = self.target_now
        else:
            coords = self.target_now.rect.center
            args_for_board.append(self.target_now)

        self.road = self.board.road_to_coords(
            tuple(map(lambda x: x // self.board.cell_size, self.rect.center)),
            tuple(map(lambda x: x // self.board.cell_size, coords)),
            *args_for_board
        )

    def set_new_checkpoint(self):
        """sets new checkpoint using road"""
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
        """moves to target"""
        if self.update_road_iter < self.update_road_int:
            self.update_road_iter += 1

        if self.target_now is None:
            return False

        if self.checkpoint is None:
            self.set_new_checkpoint()

            if isinstance(self.target_now, tuple) and list(map(lambda x: x // self.board.cell_size,
                                                               self.rect.center)) == \
                    list(map(lambda x: x // self.board.cell_size, self.target_now)):
                self.checkpoint = self.target_now
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


class Warriors(MovingEntity):
    """warriors"""

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
        self.strength = CONFIG.getint('warriors', 'Strength')
        self.speed = CONFIG.getint('warriors', 'Speed')
        self.speed_cooldown = cycle(range(self.speed + 1))
        self.attack_speed = CONFIG.getint('warriors', 'CoolDownAttack')
        self.attack_cooldown = cycle(range(self.attack_speed + 1))
        self.distance_to_attack = CONFIG.getint('warriors', 'DistanceToAttack')
        self.cost = CONFIG.getint('warriors', 'Cost')

    def get_damage(self, entity, damage: int, *args) -> bool:
        """Gets some damage and if self.target is None then self.target is Entity
        from which the damage was taken"""
        if entity != Entity and self.hp < self.max_hp * 0.40:
            self.targets.append(entity)
            self.target_now = self.targets[-1]
        return super().get_damage(entity, damage, type(self).getRussianName(), *args)

    def attack_target(self):
        """attack target and animation"""
        if self.target_now.rect.center[0] > self.rect.center[0]:
            self.looking_at = 0
        elif self.target_now.rect.center[1] > self.rect.center[1]:
            self.looking_at = 1
        elif self.target_now.rect[0] < self.rect.center[0]:
            self.looking_at = 2
        elif self.target_now.rect[1] < self.rect.center[1]:
            self.looking_at = 3

        if next(self.attack_cooldown) == self.attack_speed:
            self.image = pygame.transform.rotate(next(self.attack_images), self.looking_at * 90)

            return self.target_now.get_damage(self, self.strength)
        return False

    def move_to_target(self):
        """try to move to target"""
        if next(self.speed_cooldown) == self.speed:
            return super().move_to_target()
        return False

    def update(self):
        """check enemies near, attack and move"""
        if self.target_now is not None:
            if not isinstance(self.target_now, tuple):
                if self.target_now.hp <= 0:
                    self.target_now = None
                    del self.targets[-1]
                    return None
            if isinstance(self.target_now, tuple):
                self.move_to_target()
                if self.rect.center == self.target_now:
                    self.target_now = None
                    del self.targets[-1]
            else:
                if self.get_intersection(self.target_now, self.distance_to_attack):
                    if self.attack_target():
                        self.target_now = None
                        del self.targets[-1]
                else:
                    self.move_to_target()
        else:
            self.target_now = self.targets[-1]
            self.image = pygame.transform.rotate(next(self.standing_image), self.looking_at * 90)

    def getRussianName():
        """gets russian name"""
        return 'Воины'


class Archery(MovingEntity):
    """archery"""

    def __init__(self, spawn_coords: tuple, player: Player, board: Board, add_to_group=True):
        if add_to_group:
            super().__init__(cycle(load_images(CONFIG['archery']['Moving_images'])), player,
                             CONFIG.getint('archery', 'HP'),
                             CONFIG.getint('archery', 'HPMax'),
                             board,
                             SPRITES_GROUPS['ENTITIES'])
        else:
            super().__init__(cycle(load_images(CONFIG['archery']['Moving_images'])), player,
                             CONFIG.getint('archery', 'HP'),
                             CONFIG.getint('archery', 'HPMax'),
                             board)

        self.attack_images = cycle(load_images(CONFIG['archery']['Attacking_images']))
        self.standing_image = cycle(load_images(CONFIG['archery']['Standing_images']))

        self.image = next(self.standing_image)
        self.rect = self.image.get_rect()
        self.rect.center = spawn_coords

        self.player = player
        self.strength = CONFIG.getint('archery', 'Strength')
        self.speed = CONFIG.getint('archery', 'Speed')
        self.speed_cooldown = cycle(range(self.speed + 1))
        self.attack_speed = CONFIG.getint('archery', 'CoolDownAttack')
        self.attack_cooldown = cycle(range(self.attack_speed + 1))
        self.distance_to_attack = CONFIG.getint('archery', 'DistanceToAttack')
        self.cost = CONFIG.getint('archery', 'Cost')

    def get_damage(self, entity, damage: int, *args) -> bool:
        """Gets some damage and if self.target is None then self.target is Entity
        from which the damage was taken"""
        if entity != Entity:
            self.targets.append(entity)
            self.target_now = self.targets[-1]
        return super().get_damage(entity, damage, type(self).getRussianName(), *args)

    def attack_target(self):
        """attack target and animation"""
        if next(self.attack_cooldown) == self.attack_speed:
            self.image = pygame.transform.rotate(next(self.attack_images), self.looking_at * 90)

            return self.target_now.get_damage(self, self.strength)
        return False

    def move_to_target(self):
        """try to move to target"""
        if next(self.speed_cooldown) == self.speed:
            return super().move_to_target()
        return False

    def check_near_enemies(self):
        """check enemies"""
        for ent in SPRITES_GROUPS['ENTITIES']:
            if sqrt((ent.rect.center[0] - self.rect.center[0]) ** 2 + (
                    ent.rect.center[1] - self.rect.center[1])
                    ** 2) <= self.distance_to_attack and ent.player != self.player:
                if ent not in self.targets:
                    self.targets.append(ent)
                    self.target_now = self.targets[-1]

    def update(self):
        """update"""
        self.check_near_enemies()
        if self.target_now is not None:
            if not isinstance(self.target_now, tuple):
                if self.target_now.hp <= 0:
                    self.target_now = None
                    del self.targets[-1]
                    return None
            if isinstance(self.target_now, tuple):
                self.move_to_target()
                if self.rect.center == self.target_now:
                    self.target_now = None
                    del self.targets[-1]
            else:
                if sqrt((self.target_now.rect.center[0] - self.rect.center[0]) ** 2 + (
                        self.target_now.rect.center[1] - self.rect.center[1]) ** 2) \
                        <= self.distance_to_attack:
                    if self.attack_target():
                        self.target_now = None
                        del self.targets[-1]
                else:
                    self.move_to_target()
        else:
            self.target_now = self.targets[-1]
            self.image = pygame.transform.rotate(next(self.standing_image), self.looking_at * 90)

    def getRussianName():
        """gets russian name"""
        return 'Лучники'


class Tower(Entity):
    """tower"""

    def __init__(self, spawn_coords: tuple, player: Player, board: Board, add_to_group=True):
        self.standing_image = load_image('data/tower/standing.png')
        self.image = self.standing_image
        self.rect = self.image.get_rect()
        self.rect.center = spawn_coords
        self.lastAttacker = None

        self.player = player

        self.money = CONFIG.getint('player', 'MoneyStart')
        self.money_max = CONFIG.getint('player', 'MoneyMax')

        if add_to_group:
            super().__init__(player, CONFIG.getint('tower', 'HP'),
                             CONFIG.getint('tower', 'HPMax'), board, SPRITES_GROUPS['ENTITIES'])
        else:
            super().__init__(player, CONFIG.getint('tower', 'HP'),
                             CONFIG.getint('tower', 'HPMax'), board)

    def get_damage(self, entity, damage: int, *args) -> bool:
        """gets damage"""
        self.lastAttacker = entity
        return super().get_damage(entity, damage, type(self).getRussianName(), *args)

    def getRussianName():
        """gets russian name"""
        return 'Башня'
