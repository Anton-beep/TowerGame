import sys

import pygame
import configparser
from Spells import *
from start import *
from Players import Player, Bot
from Entities import *
from Sprites import *
import time

PLAYER = Player('blue')
BOT_ENEMY = Bot('red')

SPAWN_POINTS = {PLAYER: list(),
                BOT_ENEMY: list()}


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    pass


def player_tower(coords):
    global PLAYER_TOWER
    PLAYER_TOWER = Tower(coords, PLAYER)


def bot_tower(coords):
    global BOT_TOWER
    BOT_TOWER = Tower(coords, BOT_ENEMY)


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
                SPRITES_LEVEL[el[1]](((el[0] + 1) * cell_size, (row[0] + 1) * cell_size))


def point_collide(coords: tuple, *groups):
    ans = list()
    for el in map(lambda y: list(filter(lambda x: x.rect.collidepoint(coords), y)), groups):
        ans += el
    return ans


def spawn_entity(ent, player: Player) -> bool:
    for coords in SPAWN_POINTS[player]:
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
    yet_chose = False
    chosen_spell = ''
    pygame.init()
    pygame.display.set_caption('TowerGame')

    # start_screen()

    fps = CONFIG.getint('FPS', 'FPS')

    load_level('data/levels/level1.txt')
    for _ in range(3):
        spawn_entity(Warriors, PLAYER)
        spawn_entity(Warriors, BOT_ENEMY)
        list(SPRITES_GROUPS['ENTITIES'])[-2].target = list(SPRITES_GROUPS['ENTITIES'])[-1]
        list(SPRITES_GROUPS['ENTITIES'])[-1].target = list(SPRITES_GROUPS['ENTITIES'])[-2]
    poison = Poison_spell(SPRITES_GROUPS['SPELLS'])
    light = Lightning_spell(SPRITES_GROUPS['SPELLS'])
    while True:
        for spell in SPRITES_GROUPS['SPELLS']:
            spell.update(time.time())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed(3)[0]:
                    if yet_chose is False:
                        for spell in point_collide(event.pos, SPRITES_GROUPS['SPELLS']):
                            a = spell.select_spell(yet_chose)
                            yet_chose = True
                            chosen_spell = 'light' if a == 1 else 'poison' if a == 2 else ''
                    else:
                        if chosen_spell == 'light' and light.return_status() is True:
                            for entity in point_collide(event.pos, SPRITES_GROUPS['ENTITIES']):
                                lightning_damage = light.damage_light(time.time())
                                entity.get_damage(Entity, lightning_damage)
                                yet_chose = False
                        elif chosen_spell == 'poison' and poison.return_status() is True:
                            poison.damage_poison(time.time(), event.pos)
                            yet_chose = False

        for ent in SPRITES_GROUPS['ENTITIES']:
            if type(ent) == Warriors:
                if ent.player == PLAYER and ent.target is None:
                    ent.set_target(BOT_TOWER)
                elif ent.player == BOT_ENEMY and ent.target is None:
                    ent.set_target(PLAYER_TOWER)

        if BOT_TOWER.hp <= 0:
            print('Player wins')
            input()
        elif PLAYER_TOWER.hp <= 0:
            print('BOT wins')
            input()
        MAIN_SCREEN.fill(pygame.Color('black'))
        FORWARD_SCREEN.fill(pygame.Color('black'))

        FORWARD_SCREEN.set_colorkey((0, 0, 0))
        for ent in SPRITES_GROUPS['ENTITIES']:
            ent.update()
        for group in SPRITES_GROUPS.values():
            group.draw(FORWARD_SCREEN)
        for group in CIRCLE_SPRITES_GROUPS.values():
            group.draw(MAIN_SCREEN)
        MAIN_SCREEN.blit(FORWARD_SCREEN, (0, 0))
        CLOCK.tick(fps)
        pygame.display.flip()


if __name__ == '__main__':
    main()
