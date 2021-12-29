import os
import sys

import pygame.image
from start import SPRITES_GROUPS, CONFIG
from boards import Cell, Board


def load_images(dir):
    if not os.path.exists(dir):
        print('Dir ' + dir + ' does not exist')
        sys.exit()
    if len(os.listdir(dir)) == 0:
        print('Dir ' + dir + ' is empty')
        sys.exit()
    return list(map(lambda x: pygame.image.load(dir + "\\" + x), os.listdir(dir)))


def load_image(path):
    if not os.path.isfile(path):
        print('Image ' + path + ' does not exist')
        sys.exit()
    return pygame.image.load(path)


class Wall(pygame.sprite.Sprite, Cell):
    def __init__(self, coords, board: Board):
        super().__init__(SPRITES_GROUPS['STATIC'])
        self.image = load_image(CONFIG['wall']['wall_image'])
        self.rect = self.image.get_rect()
        self.rect.center = coords
        board.board[coords[0] // board.cell_size][coords[1] // board.cell_size] = self

    def get_int(self):
        return -1

    def update(self):
        pass
