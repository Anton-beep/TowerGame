import os
import sys

import pygame.image
from start import SPRITES_GROUPS, CONFIG
from boards import Cell, Board
from math import sqrt


def get_intersection_two_rects(rect1, rect2, dist) -> bool:
    """Checks if rect2 intersects with rect1 at the dist"""
    # 2 horizontal rects
    if pygame.Rect(rect1.left - dist, rect1.top,
                   dist * 2 + rect1.width, rect1.height).colliderect(rect2):
        return True
    # 2 vertical rects
    if pygame.Rect(rect1.left, rect1.top + dist,
                   rect1.width, dist * 2 + rect1.height).colliderect(rect2):
        return True
    # 4 circles
    circles_centers = [rect1.topleft, rect1.topright, rect1.bottomright,
                       rect1.bottomleft]
    points_rect2 = [rect2.topleft, rect2.topright, rect2.bottomright,
                    rect2.bottomleft]
    # check distance of 4 points of rect2
    for center in circles_centers:
        for point in points_rect2:
            if distance_two_points(point, center) <= dist:
                return True
    return False


def distance_two_points(point1, point2):
    return sqrt(abs(point1[0] - point2[0]) ** 2 + abs(point1[1] - point2[1]) ** 2)


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
