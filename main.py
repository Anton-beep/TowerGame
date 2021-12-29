import sys
import os
import pygame
from pprint import pprint
from collections import deque
from start import *
from Players import *
from Entities import *
from Sprites import *

MAIN_BOARD = Board((1, 1), 100, 100)

PLAYER = Player('blue')
BOT_ENEMY = Bot('red')

SPAWN_POINTS = {PLAYER: list(),
                BOT_ENEMY: list()}


def terminate():
    pygame.quit()
    sys.exit()


def player_tower(coords):
    global PLAYER_TOWER
    PLAYER_TOWER = Tower(coords, PLAYER, MAIN_BOARD)


def bot_tower(coords):
    global BOT_TOWER
    BOT_TOWER = Tower(coords, BOT_ENEMY, MAIN_BOARD)


def spawn_point_player(coords):
    SPAWN_POINTS[PLAYER].append(coords)


def spawn_point_bot(coords):
    SPAWN_POINTS[BOT_ENEMY].append(coords)


# sprites dict in level.txt files
SPRITES_LEVEL = {
    '.': None,
    'P': player_tower,
    'B': bot_tower,
    '#': Wall,
    '~': spawn_point_player,
    '!': spawn_point_bot
}


def load_level(path):
    """Loads level in SPRITES_GROUPS from path"""
    if not os.path.isfile(path):
        print(f'Level {path} not found')
        terminate()
    with open(path, 'r', encoding='utf-8') as f:
        level = list(map(lambda x: x.rstrip(), f.readlines()))
    max_width = len(max(level, key=lambda x: len(x)))
    level = list(map(lambda x: list(x) + ['.' for _ in range(len(x), max_width)], level))
    cell_size = CONFIG.getint('window_size', 'MinCellSize')
    for row in enumerate(level):
        for el in enumerate(row[1]):
            if SPRITES_LEVEL[el[1]] is not None:
                try:
                    SPRITES_LEVEL[el[1]](((el[0] + 1) * cell_size, (row[0] + 1) * cell_size))
                except TypeError:
                    SPRITES_LEVEL[el[1]](((el[0] + 1) * cell_size, (row[0] + 1) * cell_size),
                                         MAIN_BOARD)


def start_screen():
    pass


def point_collide(coords: tuple, *groups):
    ans = list()
    for el in map(lambda y: list(filter(lambda x: x.rect.collidepoint(coords), y)), groups):
        ans += el
    return ans


def spawn_entity(ent: type(Entity), player: Player):
    for coords in SPAWN_POINTS[player]:
        flag = True
        for group in SPRITES_GROUPS.values():
            if pygame.sprite.spritecollide(ent(coords, player, MAIN_BOARD, False), group, False):
                flag = False
                break
        if flag:
            ent(coords, player, MAIN_BOARD)
            return True
    return False


def main():
    pygame.init()
    pygame.display.set_caption('TowerGame')

    start_screen()

    fps = CONFIG.getint('FPS', 'FPS')

    load_level('data/levels/level1.txt')
    spawn_entity(Warriors, PLAYER)
    list(SPRITES_GROUPS['ENTITIES'])[-1].set_target(BOT_TOWER)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed(3)[0]:
                    for entity in point_collide(event.pos, SPRITES_GROUPS['ENTITIES']):
                        entity.get_damage(Entity, 100000)

        MAIN_SCREEN.fill(pygame.Color('black'))
        for ent in SPRITES_GROUPS['ENTITIES']:
            ent.update()
        for group in SPRITES_GROUPS.values():
            group.draw(MAIN_SCREEN)

        CLOCK.tick(fps)
        pygame.display.flip()


if __name__ == '__main__':
    main()
