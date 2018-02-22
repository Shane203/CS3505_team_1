import pygame
from setup import SCREEN
from constants import BLACK
pygame.init()
class Box(object):
    """
    Class to represent a box. It has an:
    - x, y, width 'w' and height 'h'
    - colour 'c'
    - size of line, default 0
    """
    def __init__(self, msg, x, y, w, h, c, s=0):
        self._msg = msg
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._c = c
        self._s = s

    def text_objects(self, text, font):
        # Renders the msg displayed in the box
        text_surface = font.render(text, True, BLACK)
        return text_surface, text_surface.get_rect()

    def set_msg(self, msg):
        self._msg = msg

    def draw(self):
        # draws the box
        pygame.draw.rect(SCREEN, self._c, (self._x, self._y, self._w, self._h),
                         self._s)
        small_text = pygame.font.Font("freesansbold.ttf", 20)
        text_surf, text_rect = self.text_objects(self._msg, small_text)
        text_rect.center = ((self._x + (self._w/2)), (self._y+(self._h/2)))
        SCREEN.blit(text_surf, text_rect)

class Button(Box):
    """
    Button class inherits from the box class.
    It has an:
    - active colour 'ac'
    - action
    """
    def __init__(self, msg, x, y, w, h, c, s, ac, action=None):
        Box.__init__(self, msg, x, y, w, h, c, s)
        self._ac = ac
        self._action = action

    def draw(self):
        # Draws the button
        # If the mouse is within the boundaries of the button it changes
        # to its active colour 'ac'
        mouse = pygame.mouse.get_pos()
        if self._x + self._w > mouse[0] > self._x and \
           self._y + self._h > mouse[1] > self._y:
            pygame.draw.rect(SCREEN, self._ac,
                             (self._x, self._y, self._w, self._h), self._s)
        else:
            pygame.draw.rect(SCREEN, self._c,
                             (self._x, self._y, self._w, self._h), self._s)
        small_text = pygame.font.Font("freesansbold.ttf", 20)
        text_surf, text_rect = self.text_objects(self._msg, small_text)
        text_rect.center = ((self._x + (self._w/2)), (self._y+(self._h/2)))
        SCREEN.blit(text_surf, text_rect)
        return None

    def click(self):
        # Determines whether the button has been clicked
        # returns None if the button hasnt been pressed and call the function
        # 'action' if it has been pressed.
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self._x + self._w > mouse[0] > self._x and self._y + self._h > mouse[1] > self._y:
            if click[0] == 1 and self._action != None:
                return self._action()
        return None
