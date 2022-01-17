"""boards"""
import numpy as np

from start import *


class Cell:
    """cell in board"""
    def get_int(self):
        """returns int for road"""
        return 0


class Empty(Cell):
    """empty cell"""
    def get_int(self):
        return 0

    def __repr__(self):
        """need to print empty cell"""
        return 'Empty'


def check_sprite(*args):
    """checks sprite"""
    collide_rect, el, i, j, int_board, exception_entities = args
    collide_rect.center = (i[1], j[1])
    if el not in exception_entities and el.rect.colliderect(collide_rect):
        try:
            if el.player == exception_entities[0].player:
                int_board[i[0][0]][j[0][0]] = -1
        except AttributeError:
            int_board[i[0][0]][j[0][0]] = -1


def calculate_elem(board_int_copy: np.ndarray, coords: np.ndarray, i: int, j: int) -> bool:
    """calculates element"""
    if board_int_copy[coords[0]][coords[1]] == 0:
        board_int_copy[coords[0]][coords[1]] = board_int_copy[i][j] + 1
        return True
    return False


def get_neighbors(cell_coords, width, height):
    """gets neighbors"""
    neighbors = list()
    x_coord, y_coord = cell_coords
    if x_coord - 1 >= 0:
        neighbors.append([x_coord - 1, y_coord])
    if y_coord - 1 >= 0:
        neighbors.append([x_coord, y_coord - 1])
    if x_coord + 1 < width:
        neighbors.append([x_coord + 1, y_coord])
    if y_coord + 1 < height:
        neighbors.append([x_coord, y_coord + 1])
    return neighbors


class Board:
    """board class"""
    def __init__(self, coords_left_top, width, height, cell_size):
        self.left = coords_left_top[0]
        self.top = coords_left_top[1]

        self.cell_size = cell_size

        self.width = width
        self.height = height
        self.board = [[Empty()] * height for _ in range(width)]

    def get_cell(self, mouse_pos):
        """returns cell on click"""
        if not self.left <= mouse_pos[0] <= self.left + self.cell_size * self.width:
            return None
        if not self.top <= mouse_pos[1] <= self.top + self.cell_size * self.height:
            return None
        return (mouse_pos[0] - self.left) // self.cell_size, \
               (mouse_pos[1] - self.top) // self.cell_size

    def get_int_board(self, collide_rect=pygame.Rect(0, 0, 1, 1), exception_entities=None):
        """returns int board of level"""
        int_board = np.zeros((self.width, self.height))
        for i in np.ndenumerate(np.arange(self.width) * self.cell_size):
            for j in np.ndenumerate(np.arange(self.height) * self.cell_size):
                for el in SPRITES_GROUPS['ENTITIES']:
                    check_sprite(collide_rect, el, i, j, int_board, exception_entities)
                for el in SPRITES_GROUPS['STATIC']:
                    check_sprite(collide_rect, el, i, j, int_board, exception_entities)

        # print(*int_board, sep='\n')
        return int_board

    def draw_map(self, start_coords, target_coords, *args):
        """returns board with wave"""
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
                        neighbors = get_neighbors([i, j], self.width, self.height)
                        for coords in neighbors:
                            if calculate_elem(board_int_copy, coords, i, j):
                                flag = True
                            if coords == list(target_coords):
                                return board_int_copy

    def road_to_coords(self, start_coords, target_coords, *args):
        """returns road"""
        board_int_copy = self.draw_map(start_coords, target_coords, *args)
        if board_int_copy is None:
            return None
        if board_int_copy[target_coords[0]][target_coords[1]] == -1:
            return None
        coords_now = target_coords
        road = [coords_now]
        while board_int_copy[road[-1][0]][road[-1][1]] != 1:
            x_coord, y_coord = coords_now
            neighbors = get_neighbors(coords_now, self.width, self.height)
            for coords in neighbors:
                if board_int_copy[coords[0]][coords[1]] == \
                        board_int_copy[x_coord][y_coord] - 1:
                    road.append(coords)
                    coords_now = coords
                    break
        # print(*list(map(lambda x: '\t'.join(map(str, x)), board_int_copy)), sep='\n')
        return road
