import pygame
from start import *


class Button(pygame.sprite.Sprite):
    def __init__(self, text, coords, size, font, text_col, button_col):
        super().__init__(SPRITES_GROUPS['BUTTONS'])
        self.text = text
        self.coords = coords
        self.size = size
        self.font = font
        self.text_col = text_col
        self.button_col = button_col

        self.text_surface = self.font.render(self.text, True, self.text_col)
        self.image = pygame.Surface(self.size)
        self.image.fill(self.button_col)
        self.image.blit(self.text_surface, (self.size[0] / 2 - self.text_surface.get_width() / 2,
                                            self.size[1] / 2 - self.text_surface.get_height() / 2))
        self.rect = self.image.get_rect()
        self.rect.topleft = coords

    def set_text(self, new):
        self.__init__(new, self.coords, self.size, self.font, self.text_col, self.button_col)


class Push_button(Button):
    def __init__(self, text, coords, size, font, text_col, button_col):
        super().__init__(text, coords, size, font, text_col, button_col)
        self.cooldown = 0

    def click(self, coords) -> bool:
        """returns True if coords on button"""
        if self.rect.collidepoint(coords) and self.cooldown == 0:
            self.cooldown = 10
            return True
        return False

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1


class Toggle_button(Button):
    def __init__(self, text, coords, size, font, text_col, button_col):
        super().__init__(text, coords, size, font, text_col, button_col)
        self.cooldown = False

    def click(self, coords) -> bool:
        """returns True if coords on button"""
        if self.rect.collidepoint(coords):
            if not self.cooldown:
                self.cooldown = not self.cooldown
                return True
        return False

    def update(self):
        pass
