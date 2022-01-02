import pygame
from start import *


class Button(pygame.sprite.Sprite):
    def __init__(self, text, coords):
        super().__init__(SPRITES_GROUPS['BUTTONS'])
        self.text = text
        self.coords = coords

    def click(self, coords) -> bool:
        """returns True if coords on button"""
        return self.rect.collidepoint(coords)


class Level_button(Button):
    def __init__(self, text, coords):
        super().__init__(text, coords)
        self.width = 100
        self.height = 20

        self.font = pygame.font.Font(None, 24)
        self.text = self.font.render(text, True, pygame.Color('white'))
        self.image = pygame.Surface((100, 20))
        self.image.fill(pygame.Color('Red'))
        self.image.blit(self.text, (self.width / 2 - self.text.get_width() / 2,
                                    self.height / 2 - self.text.get_height() / 2))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.width, self.height)