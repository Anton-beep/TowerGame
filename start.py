import configparser
import os.path

import pygame
from datetime import datetime as dt

CONFIG = configparser.ConfigParser()
CONFIG.read('config.cfg')

CLOCK = pygame.time.Clock()
pygame.font.init()
SIZE = CONFIG.getint('window_size', 'WindowWidth'), CONFIG.getint('window_size', 'WindowHeight')
flags = pygame.DOUBLEBUF
MAIN_SCREEN = pygame.display.set_mode(SIZE, flags, vsync=False)
FORWARD_SCREEN = pygame.Surface(SIZE)

SPRITES_GROUPS = {
    'ENTITIES': pygame.sprite.Group(),
    'STATIC': pygame.sprite.Group(),
    'BUTTONS': pygame.sprite.Group(),
    'SPELLS': pygame.sprite.Group(),
}

CIRCLE_SPRITES_GROUPS = {
    'POISON_CIRCLE': pygame.sprite.Group(),
    'HEAL_CIRCLE': pygame.sprite.Group()
}

ENTITIES_LIST = list()

MAP_FOR_MOVING = None

BOT_TOWER = None
PLAYER_TOWER = None

LEVEL_RECT = None

if not os.path.exists('results'):
    os.mkdir('results')
RES_FILE = open(f"results/res_{str(dt.now())[:-7].replace(' ', '_').replace(':', '+')}.txt",
                'w', encoding='utf-8')
