import configparser
import pygame

CONFIG = configparser.ConfigParser()
CONFIG.read('config.cfg')

CLOCK = pygame.time.Clock()
SIZE = CONFIG.getint('window_size', 'WindowWidth'), CONFIG.getint('window_size', 'WindowHeight')
MAIN_SCREEN = pygame.display.set_mode(SIZE)

SPRITES_GROUPS = {
    'ENTITIES': pygame.sprite.Group(),
    'STATIC': pygame.sprite.Group(),
    'BUTTONS': pygame.sprite.Group()
}

MAP_FOR_MOVING = None

BOT_TOWER = None
PLAYER_TOWER = None
