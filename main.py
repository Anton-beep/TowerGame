import sys
import os
import pygame
from pprint import pprint
from collections import deque
from start import *
from Players import *
from Entities import *
from Sprites import *
from Buttons import *

MAIN_BOARD = Board((1, 1), 100, 100)

PLAYER = Player('blue')
BOT_ENEMY = Bot('red')

SPAWN_POINTS = {PLAYER: list(),
                BOT_ENEMY: list()}

FPS = CONFIG.getint('FPS', 'FPS')

AVAILABLE_ENTITIES = [Warriors]
LEVEL_RECT = None


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
    global LEVEL_RECT
    if not os.path.isfile(path):
        print(f'Level {path} not found')
        terminate()
    with open(path, 'r', encoding='utf-8') as f:
        level = list(map(lambda x: x.rstrip(), f.readlines()))
    max_width = len(max(level, key=lambda x: len(x)))
    level = list(map(lambda x: list(x) + ['.' for _ in range(len(x), max_width)], level))
    cell_size = CONFIG.getint('window_size', 'MinCellSize')
    LEVEL_RECT = pygame.Rect(0, 0, max_width * cell_size, len(level) * cell_size)
    for row in enumerate(level):
        for el in enumerate(row[1]):
            if SPRITES_LEVEL[el[1]] is not None:
                try:
                    SPRITES_LEVEL[el[1]](((el[0] + 1) * cell_size, (row[0] + 1) * cell_size))
                except TypeError:
                    SPRITES_LEVEL[el[1]](((el[0] + 1) * cell_size, (row[0] + 1) * cell_size),
                                         MAIN_BOARD)
    print(LEVEL_RECT)


def start_screen():
    pass


def level_selection() -> str:
    """returns level path"""
    levels_buttons = list()

    i, j = 10, 10
    for level in map(lambda x: x.split('.')[0], os.listdir('data/levels')):
        levels_buttons.append(Push_button(level, (i, j), (100, 20),
                                          pygame.font.Font(None, 24),
                                          pygame.Color('White'),
                                          pygame.Color('Red')))
        i += 200
        if i > SIZE[0]:
            i = 10
            j += 50

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        if pygame.mouse.get_pressed(3)[0]:
            for button in levels_buttons:
                if button.click(pygame.mouse.get_pos()):
                    for group in SPRITES_GROUPS.values():
                        group.empty()
                    return 'data/levels/' + button.text + '.txt'

        MAIN_SCREEN.fill(pygame.Color('black'))
        for ent in SPRITES_GROUPS['ENTITIES']:
            ent.update()
        for group in SPRITES_GROUPS.values():
            group.draw(MAIN_SCREEN)

        CLOCK.tick(FPS)
        pygame.display.flip()


def playing_level(level_path):
    load_level(level_path)
    selected_entity = None
    ent_button = list()
    flag_selecting_new_target = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        if pygame.mouse.get_pressed(3)[0]:
            if flag_selecting_new_target and LEVEL_RECT.collidepoint(pygame.mouse.get_pos()):
                if selected_entity is not None:
                    flag_iter = True
                    for el in SPRITES_GROUPS['ENTITIES']:
                        if el.click(pygame.mouse.get_pos()) and el.player != selected_entity.player:
                            selected_entity.set_target(el)
                            flag_iter = False
                            break
                    if flag_iter:
                        selected_entity.set_target(pygame.mouse.get_pos())
                    flag_selecting_new_target = False

            for ent in SPRITES_GROUPS['ENTITIES']:
                if ent.click(pygame.mouse.get_pos()):
                    if ent != selected_entity:
                        selected_entity = ent
                        flag_selecting_new_target = False
                        for el in ent_button:
                            el.kill()
                        ent_button = list()
                        if selected_entity is not None and selected_entity.player == PLAYER:
                            health_but = Push_button('hp: ' + str(ent.hp), (SIZE[0] - 210, 10),
                                                     (200, 20),
                                                     pygame.font.Font(None, 24),
                                                     pygame.Color('White'),
                                                     pygame.Color('Red'))
                            ent_button.append(health_but)
                            if type(selected_entity) == Tower:
                                money_but = Push_button('money: ' + str(ent.money),
                                                        (SIZE[0] - 210, 60),
                                                        (200, 20),
                                                        pygame.font.Font(None, 24),
                                                        pygame.Color('White'),
                                                        pygame.Color('Gold'))
                                ent_button.append(money_but)
                                for el in AVAILABLE_ENTITIES:
                                    ent_button.append(
                                        Push_button('spawn ' + el.__name__,
                                                    (SIZE[0] - 210, 110),
                                                    (200, 20),
                                                    pygame.font.Font(None, 24),
                                                    pygame.Color('White'),
                                                    pygame.Color('Green')))
                                    print(str(el))
                            else:
                                target_button = Toggle_button('set new target', (SIZE[0] - 210, 60),
                                                            (120, 20),
                                                            pygame.font.Font(None, 24),
                                                            pygame.Color('White'),
                                                            pygame.Color('Green'))
                                ent_button.append(target_button)
            for el in SPRITES_GROUPS['BUTTONS']:
                if el.click(pygame.mouse.get_pos()):
                    if type(selected_entity) == Tower:
                        if el in ent_button[2:]:
                            spawn_entity(eval(el.text.split()[1]), PLAYER)
                    else:
                        if el == target_button:
                            flag_selecting_new_target = True
                            mouse_down = True

        MAIN_SCREEN.fill(pygame.Color('black'))

        if selected_entity is not None and selected_entity.player == PLAYER:
            health_but.set_text('hp: ' + str(selected_entity.hp))
            if type(selected_entity) == Tower:
                money_but.set_text('money: ' + str(selected_entity.money))

        for ent in SPRITES_GROUPS['ENTITIES']:
            ent.update()
        for button in SPRITES_GROUPS['BUTTONS']:
            button.update()
        for group in SPRITES_GROUPS.values():
            group.draw(MAIN_SCREEN)

        CLOCK.tick(FPS)
        pygame.display.flip()


def finish_screen():
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
    pygame.font.init()
    pygame.display.set_caption('TowerGame')

    start_screen()
    playing_level(level_selection())


if __name__ == '__main__':
    main()
