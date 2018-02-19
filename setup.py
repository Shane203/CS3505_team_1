import pygame
from constants import BOARD_WIDTH, BOARD_HEIGHT, BOX_SIZE, INDENT_BOARD
from pygame.locals import RESIZABLE
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = str(0) + "," + str(25)
SCREEN = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT), RESIZABLE)
pygame.display.set_caption('Ludo Board')
pygame.display.set_icon(pygame.image.load('images/desktop-backgrounds-30.jpg'))

coOrds = dict()
def create_dicts():
    """Fills the coOrds dictionary with the co-ordinates of each block on the
        board. Each block has a key value."""
    lst = [[51, 0, 1, 2, 3, 4, 18, 19, 20, 21, 22, 23],
           [50, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10, 24],
           [49, 48, 47, 46, 45, 44, 30, 29, 28, 27, 26, 25]]
    lst2 = [[10, 9, 8, 7, 6, 5, 43, 42, 41, 40, 39, 38],
            [11, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, 37],
            [12, 13, 14, 15, 16, 17, 31, 32, 33, 34, 35, 36]]
    start_y = BOX_SIZE * 5 + INDENT_BOARD
    for i in range(3):
        start_x = INDENT_BOARD
        start_y += BOX_SIZE  # Move to next row
        for j in range(12):
            coOrds[lst[i][j]] = (start_x, start_y)  # Horizontal co-ords
            coOrds[lst2[i][j]] = (start_y, start_x)  # Vertical co-ords
            start_x += BOX_SIZE
            if j == 5:  # If reaches middle, jump to other side
                start_x += BOX_SIZE * 3

