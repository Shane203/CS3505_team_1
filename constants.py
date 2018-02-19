import pygame

GENIE_BIG = pygame.image.load('images/genie_big.png')
GENIE_SMALL = pygame.image.load('images/genie.png')
LAMP_SMALL = pygame.image.load('images/lamp.png')
LAMP_BIG = pygame.image.load('images/lamp_big.png')
BLUE_PIECE = pygame.image.load('images/blue-piece.png')
GREEN_PIECE = pygame.image.load('images/green-piece.png')
YELLOW_PIECE = pygame.image.load('images/yellow-piece.png')
RED_PIECE = pygame.image.load('images/red-piece.png')
ORANGE_PIECE = pygame.image.load('images/orange-piece.png')
ORANGE_PIECE_32 = pygame.transform.scale(pygame.image.load('images/orange-piece.png'), (32, 32))

DICE_SIZE = (200, 200)
DICE_1 = pygame.transform.scale(pygame.image.load('images/dice1.gif'), DICE_SIZE)
DICE_2 = pygame.transform.scale(pygame.image.load('images/dice2.gif'), DICE_SIZE)
DICE_3 = pygame.transform.scale(pygame.image.load('images/dice3.gif'), DICE_SIZE)
DICE_4 = pygame.transform.scale(pygame.image.load('images/dice4.gif'), DICE_SIZE)
DICE_5 = pygame.transform.scale(pygame.image.load('images/dice5.gif'), DICE_SIZE)
DICE_6 = pygame.transform.scale(pygame.image.load('images/dice6.gif'), DICE_SIZE)

ROLL_TO_IMG = {1: DICE_1, 2: DICE_2, 3: DICE_3, 4: DICE_4, 5: DICE_5, 6: DICE_6}

CURRENT_DICE = DICE_1

LOW_RANGES  = {"red":0, "green":4, "yellow":8, "blue":12}#######################

BOARD_WIDTH = 1200
BOARD_HEIGHT = 800
INDENT_BOARD = 25

BOX_SIZE = 50

TOP_LEFT_X = BOX_SIZE * 6 + INDENT_BOARD
TOP_LEFT_Y = BOX_SIZE * 6 + INDENT_BOARD
CENTRE = (BOX_SIZE * 7.5 + INDENT_BOARD, BOX_SIZE * 7.5 + INDENT_BOARD)
TOP_LEFT = (TOP_LEFT_X, TOP_LEFT_Y)
BOTTOM_LEFT = (TOP_LEFT_X, TOP_LEFT_Y + BOX_SIZE * 3)
BOTTOM_RIGHT = (TOP_LEFT_X + BOX_SIZE * 3, TOP_LEFT_Y + BOX_SIZE * 3)
TOP_RIGHT = (TOP_LEFT_X + BOX_SIZE * 3, TOP_LEFT_Y)

BG = pygame.transform.scale(pygame.image.load('images/wooden.jpg'), (BOX_SIZE * 15, BOX_SIZE * 15))
STAR = pygame.transform.scale(pygame.image.load('images/star.png'), (BOX_SIZE, BOX_SIZE))
UP_ARROW = pygame.transform.scale(pygame.image.load('images/up-arrow.png'), (BOX_SIZE, BOX_SIZE))
DOWN_ARROW = pygame.transform.scale(pygame.image.load('images/down-arrow.png'), (BOX_SIZE, BOX_SIZE))
LEFT_ARROW = pygame.transform.scale(pygame.image.load('images/left-arrow.png'), (BOX_SIZE, BOX_SIZE))
RIGHT_ARROW = pygame.transform.scale(pygame.image.load('images/right-arrow.png'), (BOX_SIZE, BOX_SIZE))

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
COLOUR_CHECK = 0
CURRENT_PLAYER = None
