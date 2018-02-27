import pygame
from pygame.locals import MOUSEMOTION, KEYUP, MOUSEBUTTONUP, QUIT
from player import Player
from score import ScoreBoard
from constants import BOARD_WIDTH, BOARD_HEIGHT, INDENT_BOARD, BG, CURRENT_DICE, SCREEN
from constants import WHITE, BLACK, RED, GREEN, BLUE, YELLOW
from constants import GENIE_BIG, LAMP_BIG, LOW_RANGES
from constants import RED_PIECE, GREEN_PIECE, YELLOW_PIECE, BLUE_PIECE
from setup import create_dicts, coOrds
from piece import Piece
from sys import exit

def endScreen(all_pieces):
    pygame.display.set_caption("End Screen")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 100)    
    x=ScoreBoard(all_pieces)
    while not pygame.event.get(QUIT):
        SCREEN.fill(WHITE)
        text = font.render("Final Score:", True, GREEN)
        text_rect = text.get_rect()
        text_x = SCREEN.get_width() / 2 - text_rect.width / 2
        text_y = SCREEN.get_height() / 2 - text_rect.height / 2
        SCREEN.blit(text, [text_x, text_y])
        x.draw(x=text_x,y=text_y+80,w=200)
        font=pygame.font.SysFont("Comicsansms",100)
        SCREEN.blit(text, [text_x, text_y])
        pygame.display.flip()
    pygame.quit()
    exit(0)

