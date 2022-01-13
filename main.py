import sys
import os
import pygame
from pprint import pprint
from collections import deque
from random import choice
from start import *
from Players import *
from Entities import *
from Sprites import *
from Buttons import *
from Spells import *
import threading
from PIL import Image
from math import ceil

PLAYER = Player('blue')
BOT_ENEMY = Bot('red')

SPAWN_POINTS = {PLAYER: list(),
                BOT_ENEMY: list()}

FPS = CONFIG.getint('FPS', 'FPS')

AVAILABLE_ENTITIES = [Warriors]

MAIN_BOARD = None


class Tread(threading.Thread):
    def __init__(self, ent):
        super().__init__(name='bib')
        self.ent = ent

    def run(self):
        self.ent.update()


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


def generateAndSetBackGroundLevel():
    global BACKGROUND
    images = list(map(lambda x: Image.open('data/backgroundImg/' + x),
                      os.listdir('data/backgroundImg')))
    img = Image.new('RGB', LEVEL_RECT.size, 'black')
    for i in range(0, LEVEL_RECT.width, CONFIG.getint('window_size', 'CellLevel')):
        for j in range(0, LEVEL_RECT.height, CONFIG.getint('window_size', 'CellLevel')):
            img.paste(choice(images), (i, j))

    img.save('data/background.png')
    BACKGROUND = pygame.sprite.Sprite()
    BACKGROUND.image = pygame.image.load('data/background.png')
    BACKGROUND.rect = LEVEL_RECT.copy()
    BACKGROUND = pygame.sprite.Group(BACKGROUND)


def load_level(path):
    """Loads level in SPRITES_GROUPS from path"""
    global LEVEL_RECT
    global MAIN_BOARD
    if not os.path.isfile(path):
        print(f'Level {path} not found')
        terminate()
    with open(path, 'r', encoding='utf-8') as f:
        level = list(map(lambda x: x.rstrip(), f.readlines()))
    max_width = len(max(level, key=lambda x: len(x)))
    level = list(map(lambda x: list(x) + ['.' for _ in range(len(x), max_width)], level))

    cell_size = CONFIG.getint('window_size', 'CellLevel')
    cell_size_board = CONFIG.getint('window_size', 'CellSizeBoard')

    board_width = len(level)
    board_height = len(level[0])
    MAIN_BOARD = Board((cell_size / 2, cell_size / 2), board_height, board_width, cell_size_board)

    LEVEL_RECT = pygame.Rect(cell_size / 2, cell_size / 2,
                             max_width * cell_size, len(level) * cell_size)
    for row in enumerate(level):
        for el in enumerate(row[1]):
            if SPRITES_LEVEL[el[1]] is not None:

                try:
                    SPRITES_LEVEL[el[1]](((el[0] + 1) * cell_size, (row[0] + 1) * cell_size))
                except TypeError:
                    SPRITES_LEVEL[el[1]](((el[0] + 1) * cell_size, (row[0] + 1) * cell_size),
                                         MAIN_BOARD)
    generateAndSetBackGroundLevel()


def start_screen():
    pass


def level_selection() -> str:
    """returns level path"""
    levels_buttons = list()

    i, j = 10, 10
    for level in sorted(map(lambda x: x.split('.')[0], os.listdir('data/levels'))):
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
    yet_chose = False
    chosen_spell = ''
    load_level(level_path)
    selected_entity = None
    ent_button = list()
    flag_selecting_new_target = False
    running = True
    poison = Poison_spell(SPRITES_GROUPS['SPELLS'])
    light = Lightning_spell(SPRITES_GROUPS['SPELLS'])
    heal = Heal_spell(SPRITES_GROUPS['SPELLS'])

    while running:
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
                            chosen_spell = 'light' if a == 1 else 'poison' if a == 2 else 'heal'
                    else:
                        if chosen_spell == 'light' and light.return_status() is True:
                            for entity in point_collide(event.pos, SPRITES_GROUPS['ENTITIES']):
                                if entity.player == BOT_ENEMY:
                                    PLAYER_TOWER.money -= light.cost
                                    lightning_damage = light.damage_light(time.time())
                                    entity.get_damage(Entity, lightning_damage)
                                    yet_chose = False
                        elif chosen_spell == 'poison' and poison.return_status() is True:
                            PLAYER_TOWER.money -= poison.cost
                            poison.damage_poison(time.time(), event.pos)
                            yet_chose = False
                        elif chosen_spell == 'heal' and poison.return_status() is True:
                            PLAYER_TOWER.money -= heal.cost
                            heal.damage_poison(time.time(), event.pos)
                            yet_chose = False

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
                    target_button.reset_cooldown()

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
                            entity_type = eval(el.text.split()[1])
                            if PLAYER_TOWER.money - entity_type(
                                    (0, 0), None, None, False).cost >= 0:
                                spawn_ent = spawn_entity(entity_type, PLAYER)
                                if spawn_ent:
                                    PLAYER_TOWER.money -= spawn_ent.cost
                    else:
                        if el == target_button:
                            flag_selecting_new_target = True

        MAIN_SCREEN.fill(pygame.Color('black'))

        if selected_entity is not None and selected_entity.player == PLAYER:
            health_but.set_text('hp: ' + str(selected_entity.hp))
            if type(selected_entity) == Tower:
                money_but.set_text('money: ' + str(selected_entity.money))

        rand_ent = choice(AVAILABLE_ENTITIES)
        if BOT_ENEMY.spawn_entity(SPRITES_GROUPS['ENTITIES'], rand_ent, BOT_TOWER.money):
            spawn_ent = spawn_entity(rand_ent, BOT_ENEMY)
            if spawn_ent is not False:
                spawn_ent.set_target(PLAYER_TOWER)
                BOT_TOWER.money -= spawn_ent.cost

        if PLAYER_TOWER.hp <= 0:
            finish_button = Push_button('BOT WINS',
                                        (SIZE[0] - SIZE[0] / 2, 500),
                                        (300, 100),
                                        pygame.font.Font(None, 30),
                                        pygame.Color('White'),
                                        pygame.Color('Red'))
            for sprite in CIRCLE_SPRITES_GROUPS['POISON_CIRCLE']:
                sprite.kill()
            for sprite in CIRCLE_SPRITES_GROUPS['HEAL_CIRCLE']:
                sprite.kill()
            running = False
        elif BOT_TOWER.hp <= 0:
            finish_button = Push_button('PLAYER WINS',
                                        (SIZE[0] - SIZE[0] / 2, 500),
                                        (300, 100),
                                        pygame.font.Font(None, 30),
                                        pygame.Color('White'),
                                        pygame.Color('Red'))
            for sprite in CIRCLE_SPRITES_GROUPS['POISON_CIRCLE']:
                sprite.kill()
            for sprite in CIRCLE_SPRITES_GROUPS['HEAL_CIRCLE']:
                sprite.kill()
            running = False

        MAIN_SCREEN.fill(pygame.Color('black'))
        BACKGROUND.draw(MAIN_SCREEN)
        FORWARD_SCREEN.fill(pygame.Color('black'))

        FORWARD_SCREEN.set_colorkey((0, 0, 0))

        threads = []
        for ent in SPRITES_GROUPS['ENTITIES']:
            threads.append(Tread(ent))

            # try:
            #     for coords in ent.road:
            #         pygame.draw.circle(MAIN_SCREEN, pygame.Color('RED'), (coords[0] * MAIN_BOARD.cell_size,
            #                                                               coords[1] * MAIN_BOARD.cell_size), 2)
            # except Exception:
            #     pass

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        for button in SPRITES_GROUPS['BUTTONS']:
            button.update()
        for group in SPRITES_GROUPS.values():
            group.draw(FORWARD_SCREEN)
        for group in CIRCLE_SPRITES_GROUPS.values():
            group.draw(MAIN_SCREEN)
        MAIN_SCREEN.blit(FORWARD_SCREEN, (0, 0))

        CLOCK.tick(FPS)
        pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        if pygame.mouse.get_pressed(3)[0]:
            if finish_button.click(pygame.mouse.get_pos()):
                running = False

    running = True
    for group in SPRITES_GROUPS.values():
        for el in group:
            el.kill()


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
            if not pygame.sprite.spritecollide(ent(coords, player,
                                                   MAIN_BOARD, False), group, False)\
                    in [[]]:
                flag = False
                break
        if flag:
            ent = ent(coords, player, MAIN_BOARD)
            return ent
    return False


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('TowerGame')

    start_screen()
    while True:
        playing_level(level_selection())


if __name__ == '__main__':
    main()
