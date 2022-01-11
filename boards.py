import pygame
import numpy as np

from start import *
from pprint import pprint
from time import time
from numba import jit, njit
import threading


class Cell:
    def get_int(self):
        return 0


class Empty(Cell):
    def get_int(self):
        return 0

    def __repr__(self):
        return 'Empty'


def check_sprite(collide_rect, el, i, j, int_board, exception_entities):
    collide_rect.center = (i[1], j[1])
    if el.rect.colliderect(collide_rect) and el not in exception_entities:
        int_board[i[0][0]][j[0][0]] = -1


def calculate_elem(board_int_copy, coords, i, j):
    if board_int_copy[coords[0]][coords[1]] == 0:
        board_int_copy[coords[0]][coords[1]] = board_int_copy[i][j] + 1
        return True
    return False


class Board:
    def __init__(self, coords_left_top, width, height):
        self.left = coords_left_top[0]
        self.top = coords_left_top[1]

        self.cell_size = CONFIG.getint('window_size', 'MinCellSize')

        self.width = width
        self.height = height
        self.board = [[Empty()] * height for _ in range(width)]

    def get_cell(self, mouse_pos):
        if not (self.left <= mouse_pos[0] <= self.left + self.cell_size * self.width):
            return None
        if not (self.top <= mouse_pos[1] <= self.top + self.cell_size * self.height):
            return None
        return (mouse_pos[0] - self.left) // self.cell_size, \
               (mouse_pos[1] - self.top) // self.cell_size

    def get_int_board(self, collide_rect=pygame.Rect(0, 0, 1, 1), exception_entities=None):
        int_board = np.array(list(map(lambda x: list(map(lambda y: y.get_int(), x)), self.board)))
        for i in np.ndenumerate(np.arange(self.width) * self.cell_size):
            for j in np.ndenumerate(np.arange(self.height) * self.cell_size):
                for el in SPRITES_GROUPS['ENTITIES']:
                    check_sprite(collide_rect, el, i, j, int_board, exception_entities)
                for el in SPRITES_GROUPS['STATIC']:
                    check_sprite(collide_rect, el, i, j, int_board, exception_entities)

        # print(*int_board, sep='\n')
        return int_board

    def draw_map(self, start_coords, target_coords, *args):
        exceptions = list()
        collide_rect = args[0].rect.copy()
        exceptions = args
        board_int_copy = self.get_int_board(collide_rect, exceptions)
        board_int_copy[start_coords[0]][start_coords[1]] = 1
        flag = True
        while flag:
            flag = False
            for i in np.arange(len(board_int_copy)):
                for j in np.arange(len(board_int_copy[i])):
                    if not board_int_copy[i][j] in (-1, 0):
                        neighbors = self.get_neighbors([i, j])
                        for coords in neighbors:
                            if calculate_elem(board_int_copy, coords, i, j):
                                flag = True
                            if coords == list(target_coords):
                                return board_int_copy

    def get_neighbors(self, cell_coords):
        neighbors = list()
        x, y = cell_coords
        if x - 1 >= 0:
            neighbors.append([x - 1, y])
        if y - 1 >= 0:
            neighbors.append([x, y - 1])
        if x + 1 < self.width:
            neighbors.append([x + 1, y])
        if y + 1 < self.height:
            neighbors.append([x, y + 1])
        return neighbors

    def road_to_coords(self, start_coords, target_coords, *args):
        board_int_copy = self.draw_map(start_coords, target_coords, *args)
        if board_int_copy is None:
            return None
        coords_now = target_coords
        road = [coords_now]
        while board_int_copy[road[-1][0]][road[-1][1]] != 1:
            x, y = coords_now
            neighbors = self.get_neighbors(coords_now)
            for coords in neighbors:
                if board_int_copy[coords[0]][coords[1]] == \
                        board_int_copy[x][y] - 1:
                    road.append(coords)
                    coords_now = coords
                    break
        # print(*list(map(lambda x: '\t'.join(map(str, x)), board_int_copy)), sep='\n')
        return road
