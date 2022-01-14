import configparser
import pygame

CONFIG = configparser.ConfigParser()
CONFIG.read('config.cfg')

CLOCK = pygame.time.Clock()
pygame.font.init()
SIZE = CONFIG.getint('window_size', 'WindowWidth'), CONFIG.getint('window_size', 'WindowHeight')
MAIN_SCREEN = pygame.display.set_mode(SIZE)
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
