import pygame
from start import *
from Sprites import load_image


class Button(pygame.sprite.Sprite):
    def __init__(self, text, coords, text_col,
                 button_col=load_image('data/buttonsImg/button1.png'), font=pygame.font.Font(None, 26), size=None):
        super().__init__(SPRITES_GROUPS['BUTTONS'])
        self.text = text
        self.coords = coords
        self.font = font
        self.text_col = text_col

        self.text_surface = self.font.render(self.text, True, self.text_col)
        if size is None:
            self.size = (self.text_surface.get_width() + 20, self.text_surface.get_height())
        else:
            self.size = size
        if type(button_col) == pygame.Color:
            self.button_col = button_col
            self.image = pygame.Surface(self.size)
            self.image.fill(self.button_col)
        else:
            self.button_col = button_col
            self.image = pygame.transform.scale(button_col, self.text_surface.get_size())
        self.image.blit(self.text_surface, (self.size[0] / 2 - self.text_surface.get_width() / 2,
                                            self.size[1] / 2 - self.text_surface.get_height() / 2))
        self.rect = self.image.get_rect()
        self.rect.topleft = coords

    def set_text(self, new):
        self.__init__(new, self.coords, self.text_col, self.button_col)


class Push_button(Button):
    def __init__(self, *args):
        super().__init__(*args)
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
    def __init__(self, *args):
        self.args = args
        super().__init__(*args)
        self.cooldown = False
        self.cooldownTime = 0

    def click(self, coords) -> bool:
        """returns True if coords on button"""
        if self.cooldownTime == 10:
            if self.rect.collidepoint(coords):
                self.cooldown = not self.cooldown
                self.cooldownTime = 0
                if self.cooldown:
                    if len(self.args) >= 4:
                        super().__init__(*list(list(self.args)[:3] +
                                         [pygame.Color(self.args[3][0] // 2, self.args[3][1] // 2,
                                                       self.args[3][2] // 2)]))
                    return True
                else:
                    super().__init__(*self.args)
        else:
            self.cooldownTime += 1
            return False

    def reset_cooldown(self):
        """resets self.cooldown to default False"""
        self.cooldown = False
        super().__init__(*self.args)

    def update(self):
        pass
