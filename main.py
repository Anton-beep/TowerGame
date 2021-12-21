import pygame
import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read('config.cfg')

CLOCK = pygame.time.Clock()
SIZE = list(map(int, [CONFIG['window_size']['WindowWidth'],
                      CONFIG['window_size']['WindowHeight']]))
MAIN_SCREEN = pygame.display.set_mode(SIZE)

SPRITES_GROUPS = {
    'ENTITIES': pygame.sprite.Group(),
    'STATIC': pygame.sprite.Group()
}


def main():
    pygame.init()
    pygame.display.set_caption('TowerGame')


if __name__ == '__main__':
    main()
