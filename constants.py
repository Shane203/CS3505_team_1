import pygame
from pygame.locals import RESIZABLE

BOARD_WIDTH = 1200
BOARD_HEIGHT = 800
INDENT_BOARD = 25

BOX_SIZE = 50

pygame.init()

#Need Screen here to use .convert_alpha()
SCREEN = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT), RESIZABLE)

pieceMove_sound = pygame.mixer.Sound('sound/Move.wav')
rollDice_sound = pygame.mixer.Sound('sound/Dice.wav')
kill_sound = pygame.mixer.Sound('sound/Kill.wav')
win_sound = pygame.mixer.Sound('sound/Win.wav')
first_sound = pygame.mixer.Sound('sound/First.wav')
noMove_sound = pygame.mixer.Sound('sound/NoMove.wav')

SOUND_OPEN = pygame.image.load('images/sound_open.png')
SOUND_MUTE = pygame.image.load('images/sound_mute.png')

GENIE_BIG = pygame.image.load('images/genie_big.png').convert_alpha()
GENIE_SMALL = pygame.image.load('images/genie.png').convert_alpha()
LAMP_SMALL = pygame.image.load('images/lamp.png').convert_alpha()
LAMP_BIG = pygame.image.load('images/lamp_big.png').convert_alpha()
BLUE_PIECE = pygame.image.load('images/blue-piece.png').convert_alpha()
GREEN_PIECE = pygame.image.load('images/green-piece.png').convert_alpha()
YELLOW_PIECE = pygame.image.load('images/yellow-piece.png').convert_alpha()
RED_PIECE = pygame.image.load('images/red-piece.png').convert_alpha()
ORANGE_PIECE = pygame.image.load('images/orange-piece.png').convert_alpha()
ORANGE_PIECE_32 = pygame.transform.scale(pygame.image.load('images/orange-piece.png').convert_alpha(), (32, 32))

DICE_SIZE = (200, 200)
DICE_1 = pygame.transform.scale(pygame.image.load('images/dice1.gif').convert_alpha(), DICE_SIZE)
DICE_2 = pygame.transform.scale(pygame.image.load('images/dice2.gif').convert_alpha(), DICE_SIZE)
DICE_3 = pygame.transform.scale(pygame.image.load('images/dice3.gif').convert_alpha(), DICE_SIZE)
DICE_4 = pygame.transform.scale(pygame.image.load('images/dice4.gif').convert_alpha(), DICE_SIZE)
DICE_5 = pygame.transform.scale(pygame.image.load('images/dice5.gif').convert_alpha(), DICE_SIZE)
DICE_6 = pygame.transform.scale(pygame.image.load('images/dice6.gif').convert_alpha(), DICE_SIZE)

ROLL_TO_IMG = {1: DICE_1, 2: DICE_2, 3: DICE_3, 4: DICE_4, 5: DICE_5, 6: DICE_6}

CURRENT_DICE = DICE_1

LOW_RANGES  = {"red":0, "green":4, "yellow":8, "blue":12}#######################

TOP_LEFT_X = BOX_SIZE * 6 + INDENT_BOARD
TOP_LEFT_Y = BOX_SIZE * 6 + INDENT_BOARD
CENTRE = (BOX_SIZE * 7.5 + INDENT_BOARD, BOX_SIZE * 7.5 + INDENT_BOARD)
TOP_LEFT = (TOP_LEFT_X, TOP_LEFT_Y)
BOTTOM_LEFT = (TOP_LEFT_X, TOP_LEFT_Y + BOX_SIZE * 3)
BOTTOM_RIGHT = (TOP_LEFT_X + BOX_SIZE * 3, TOP_LEFT_Y + BOX_SIZE * 3)
TOP_RIGHT = (TOP_LEFT_X + BOX_SIZE * 3, TOP_LEFT_Y)

BG = pygame.transform.scale(pygame.image.load('images/wooden.jpg').convert_alpha(), (BOX_SIZE * 15, BOX_SIZE * 15))
STAR = pygame.transform.scale(pygame.image.load('images/star.png').convert_alpha(), (BOX_SIZE, BOX_SIZE))
UP_ARROW = pygame.transform.scale(pygame.image.load('images/up-arrow.png').convert_alpha(), (BOX_SIZE, BOX_SIZE))
DOWN_ARROW = pygame.transform.scale(pygame.image.load('images/down-arrow.png').convert_alpha(), (BOX_SIZE, BOX_SIZE))
LEFT_ARROW = pygame.transform.scale(pygame.image.load('images/left-arrow.png').convert_alpha().convert_alpha(), (BOX_SIZE, BOX_SIZE))
RIGHT_ARROW = pygame.transform.scale(pygame.image.load('images/right-arrow.png').convert_alpha(), (BOX_SIZE, BOX_SIZE))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0) #ff0000
GREEN = (0, 150, 0) #009600
BLUE = (50, 50, 255) #3232ff
YELLOW = (254, 244, 38) #fef426
ORANGE = (250, 102, 10) #FA660A
LGREEN = (102, 255, 102) 
LYELLOW = (255, 255, 204) 
LBLUE = (0, 204, 255) 
BRIGHTGREEN = (0, 255, 0) #00FF00

FPS = 10
COLOUR_TO_IMG = {"red": RED_PIECE, "green": GREEN_PIECE, "yellow": YELLOW_PIECE, "blue": BLUE_PIECE}

FLASH_RATE = FPS * 8
IN = 1
pygame.quit()
