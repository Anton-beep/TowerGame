from start import *
from pprint import pprint


class Cell:
    def get_int(self):
        return 0


class Empty(Cell):
    def get_int(self):
        return 0

    def __repr__(self):
        return 'Empty'


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

    def get_int_board(self, exception_ent=None):
        int_board = self.board.copy()
        for i in enumerate(list(map(lambda x: x * self.cell_size, range(self.width)))):
            for j in enumerate(list(map(lambda y: y * self.cell_size, range(self.height)))):
                flag = True
                for group in SPRITES_GROUPS.values():
                    for el in group:
                        if el.rect.collidepoint(i[1], j[1]) and el != exception_ent:
                            flag = False
                            int_board[i[0]][j[0]] = -1
                if flag:
                    int_board[i[0]][j[0]] = 0

        return int_board

    def draw_map(self, start_coords, target_coords):
        exception = None
        for el in SPRITES_GROUPS['ENTITIES']:
            if el.rect.collidepoint(list(map(lambda x: x * self.cell_size, target_coords))):
                exception = el
                break
        board_int_copy = self.get_int_board(exception)
        board_int_copy[start_coords[0]][start_coords[1]] = 1
        flag = True
        while flag:
            flag = False
            for i in range(len(board_int_copy)):
                for j in range(len(board_int_copy[i])):
                    if not board_int_copy[i][j] in (-1, 0):
                        neighbors = self.get_neighbors([i, j])
                        for coords in neighbors:
                            try:
                                if board_int_copy[coords[0]][coords[1]] == 0:
                                    flag = True
                                    board_int_copy[coords[0]][coords[1]] = board_int_copy[i][j] + 1
                                    if coords == list(target_coords):
                                        return board_int_copy
                            except Exception:
                                pass

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

    def road_to_coords(self, start_coords, target_coords):
        board_int_copy = self.draw_map(start_coords, target_coords)
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