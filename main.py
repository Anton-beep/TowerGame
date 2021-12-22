import sys

import pygame
import configparser
from start import *
from Players import Player, Bot
from Entities import *
from Sprites import *

PLAYER = Player('blue')
BOT_ENEMY = Bot('red')


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    pass


def Player_tower(coords):
    tower = Tower(coords, PLAYER)
    SPRITES_GROUPS['ENTITIES'].add(tower)
    ENTITIES_LIST.append(tower)


def Bot_tower(coords):
    tower = Tower(coords, BOT_ENEMY)
    SPRITES_GROUPS['ENTITIES'].add(tower)
    ENTITIES_LIST.append(tower)


def wall(coords):
    SPRITES_GROUPS['STATIC'].add(Wall(coords))


# sprites dict in level.txt files
SPRITES_LEVEL = {
    '.': None,
    'P': Player_tower,
    'B': Bot_tower,
    '#': Wall
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
                SPRITES_LEVEL[el[1]](((el[0] + 1) * cell_size, (row[0] + 1) * cell_size))


def main():
    pygame.init()
    pygame.display.set_caption('TowerGame')

    # start_screen()

    fps = CONFIG.getint('FPS', 'FPS')

    load_level('data/levels/level1.txt')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                flag = False
                for entity in SPRITES_GROUPS['ENTITIES']:
                    if entity.rect.collidepoint(event.pos):
                        if entity.get_damage(Entity, 10000000):
                            entity.kill()
                        flag = True
                if not flag:
                    Warriors(event.pos, PLAYER)

        MAIN_SCREEN.fill(pygame.Color('black'))
        for group in SPRITES_GROUPS.values():
            group.draw(MAIN_SCREEN)

        CLOCK.tick(fps)
        pygame.display.flip()


if __name__ == '__main__':
    main()
