# Team 1
import pygame
from Team_1_constants import SCREEN
from Team_1_constants import BLACK
pygame.init()


class Box(object):
    """
    This class is used to produce boxes to represent information to players

    :param msg: Message to appear in the box.
    :param x: x coordinate of the top left-hand corner of the box.
    :type x: int
    :param y: y coordinate of the top left-hand corner of the box.
    :type y: int
    :param w: width of the box.
    :type w: int
    :param h: height of the box.
    :type h: int
    :param c: colour of the box
    :type c: str
    :param s: size of the border line of the box, default 0.
    :type s: int

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
        """Renders the msg displayed in the box.

        :param text: text to be rendered on the surface.
        :type text: str
        :param font: font of the text.
        :type font: str
        :return text_surface: ``text_surface`` is the surface the text
                to be displayed on.
        :return text_surface.get_rect(): ``text_surface.get_rect()`` is the
                rectangle containing the surface with the text.
        """
        text_surface = font.render(text, True, BLACK)
        return text_surface, text_surface.get_rect()

    def set_msg(self, msg):
        """Sets the box's message.

        :param msg: Message to be displayed in the box.
        :type msg: str
        """
        self._msg = msg

    def draw(self):
        """Draws the box which will display information to the player."""
        pygame.draw.rect(SCREEN, self._c, (self._x, self._y, self._w, self._h),
                         self._s)
        small_text = pygame.font.SysFont("arialblack", 20)
        text_surf, text_rect = self.text_objects(self._msg, small_text)
        text_rect.center = ((self._x + (self._w/2)), (self._y+(self._h/2)))
        SCREEN.blit(text_surf, text_rect)


class Button(Box):
    """
    Button class inherits from the box class.

    Args:
        :arg ac: active colour. The colour of the box when the mouse hovers
                   over it.
        :arg action: method called when the button is clicked, default = None.
    """
    def __init__(self, msg, x, y, w, h, c, s, ac, action=None):
        Box.__init__(self, msg, x, y, w, h, c, s)
        self._ac = ac
        self._action = action

    def draw(self):
        """Draws the button. If the mouse is within the boundaries of the button
        it changes to its active colour 'ac'.

        """
        # This is the location of the mouse [x, y].
        mouse = pygame.mouse.get_pos()
        if self._x + self._w > mouse[0] > self._x and \
           self._y + self._h > mouse[1] > self._y:
            pygame.draw.rect(SCREEN, self._ac,
                             (self._x, self._y, self._w, self._h), self._s)
        else:
            pygame.draw.rect(SCREEN, self._c,
                             (self._x, self._y, self._w, self._h), self._s)
        small_text = pygame.font.SysFont("arialblack", 20)
        text_surf, text_rect = self.text_objects(self._msg, small_text)
        text_rect.center = ((self._x + (self._w/2)), (self._y+(self._h/2)))
        SCREEN.blit(text_surf, text_rect)

    def click(self):
        """Determines whether the button has been clicked.

        :return: None if the button hasn't been pressed and calls the function
                'action' if it has been pressed.

        """
        mouse = pygame.mouse.get_pos()  # Is the location of the mouse [x, y]
        # click: Is the location of the click.x coordinate, y coordinate and
        # whether it was the right or left press [x, y, r/h]
        click = pygame.mouse.get_pressed()
        if self._x + self._w > mouse[0] > self._x and self._y + self._h > \
                mouse[1] > self._y:
            if click[0] == 1 and self._action is not None:
                return self._action()
        return None
