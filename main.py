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


def player_tower(coords):
    tower = Tower(coords, PLAYER)
    SPRITES_GROUPS['ENTITIES'].add(tower)
    ENTITIES_LIST.append(tower)


def bot_tower(coords):
    tower = Tower(coords, BOT_ENEMY)
    SPRITES_GROUPS['ENTITIES'].add(tower)
    ENTITIES_LIST.append(tower)


def spawn_point(coords):
    SPAWN_POINTS.append(coords)


# sprites dict in level.txt files
SPRITES_LEVEL = {
    '.': None,
    'P': player_tower,
    'B': bot_tower,
    '#': Wall,
    '~': spawn_point
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


def point_collide(coords: tuple, *groups):
    ans = list()
    for el in map(lambda y: list(filter(lambda x: x.rect.collidepoint(coords), y)), groups):
        ans += el
    return ans


def spawn_entity(ent, player: Player) -> bool:
    for coords in SPAWN_POINTS:
        flag = True
        for group in SPRITES_GROUPS.values():
            if pygame.sprite.spritecollide(ent(coords, player, False), group, False):
                flag = False
                break
        if flag:
            ent(coords, player)
            return True
    return False



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
                if pygame.mouse.get_pressed(3)[0]:
                    for entity in point_collide(event.pos, SPRITES_GROUPS['ENTITIES']):
                        entity.get_damage(Entity, 100000)
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    print('bib')
                    spawn_entity(Warriors, PLAYER)

        MAIN_SCREEN.fill(pygame.Color('black'))
        for group in SPRITES_GROUPS.values():
            group.draw(MAIN_SCREEN)

        CLOCK.tick(fps)
        pygame.display.flip()


if __name__ == '__main__':
    main()
