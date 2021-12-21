import os
import sys

import pygame.image


def load_image(path):
    if not os.path.isfile(path):
        print(f'Image {path} does not exist')
        sys.exit()
    return pygame.image.load(path)