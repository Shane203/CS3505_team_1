import sys
import time
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
import _thread
import pygame
from piece import Piece
from pygame.locals import MOUSEMOTION, KEYUP, MOUSEBUTTONUP, QUIT
from player import Player
from score import ScoreBoard
from constants import BOARD_WIDTH, BOARD_HEIGHT, INDENT_BOARD, BG, CURRENT_DICE
from constants import WHITE, BLACK, RED, GREEN, BLUE, YELLOW
from constants import FPS, FLASH_RATE
from constants import GENIE_BIG, LAMP_BIG, LOW_RANGES
from constants import RED_PIECE, GREEN_PIECE, YELLOW_PIECE, BLUE_PIECE
from setup import SCREEN, create_dicts, coOrds
from board import Board
from connection import Connection

class Ludo(object):
    def __init__(self):
        self.my_player = None
        self.genie_owner = None
        self.starting_point = {"red": 0, "green": 13, "yellow": 26, "blue": 39}
        self.cs = ["red", "green", "yellow", "blue"]
        self.colour_to_img = {"red": RED_PIECE, "green": GREEN_PIECE, "yellow": YELLOW_PIECE, "blue": BLUE_PIECE}
        self.all_pieces = [Piece(self.cs[c], num, self.colour_to_img[self.cs[c]], self.starting_point[self.cs[c]]) for c in range(4) for num in range(1, 5)]
        self.board = Board(self.genie_owner, self.my_player, self.all_pieces, self.colour_to_img)
        self.connection = Connection(self.board, self.my_player, None, self.all_pieces)
        self.current_player = self.connection.current_player
        self.clock = pygame.time.Clock()
        self.score = ScoreBoard()
        self.IN = 1
        self.colour_check = 0
        
    def setup(self):
        create_dicts()
        pygame.init()
        pygame.event.set_blocked([MOUSEMOTION, KEYUP, MOUSEBUTTONUP])
        self.board.add_connection(self.connection)
        self.connection.connect_to_server()
        self.show_start_screen()

    def terminate(self):
        pygame.quit()
        sys.exit()

    def click_piece(self, num, piece):
        self.board.move_piece(num, self.connection.my_player.roll)
        print("piece moved. rolls:", self.connection.my_player.rollsleft, "-turnstaken:", self.connection.my_player.turnstaken)
        if self.connection.my_player.roll != 0:
            self.connection.my_player.turnstaken += 1 #Player moved piece, increase turnstaken
            print("piece moved after update rolls:", self.connection.my_player.rollsleft, "-turnstaken:", self.connection.my_player.turnstaken)
            self.connection.send_movement(num, self.connection.my_player.roll)
        if self.connection.my_player.turnstaken == 3 or self.connection.my_player.rollsleft == 0: #End turn if player has no rolls left, or they've already taken 3 turns.
            _thread.start_new_thread(self.connection.end_turn, ()) 
        else:
            self.connection.my_player.roll = 0
        print("Outside", piece.get_steps_from_start())

    def show_start_screen(self):
        FPSCLOCK = pygame.time.Clock()
        title_font = pygame.font.SysFont("Arial", 100)
        colours = [RED, GREEN, YELLOW, BLUE]
        index = 0
        while True:
            SCREEN.fill(WHITE)
            title_surf = title_font.render('Ludo!', True, colours[index])
            title_surf_rect = title_surf.get_rect()
            title_surf_rect.center = (BOARD_WIDTH / 2, BOARD_HEIGHT / 2)
            SCREEN.blit(title_surf, title_surf_rect)

            if self.connection.my_player is not None:
                pygame.event.get()
                return
            if pygame.event.get(QUIT):
                self.terminate()
            index = (index + 1) % 4
            pygame.display.update()
            FPSCLOCK.tick(5)

    def run(self):
        while True:
            try:
                SCREEN.fill(WHITE)
                SCREEN.blit(BG, (INDENT_BOARD, INDENT_BOARD))
                self.board.draw_board(self.colour_check)
                self.colour_check = (self.colour_check + 1) % FLASH_RATE
                self.score.draw(self.all_pieces)
                self.board.PLAYER_FIELD.draw()
                OUTPUT = self.board.ROLL_BUTTON.draw()
                if OUTPUT is not None:
                    self.board.dice_object.dice.roll_dice_gif(OUTPUT, self.IN, 900, 230)
                self.board.dice_object.display_dice(900, 230, self.connection.current_dice)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.terminate()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a:
                            self.board.move_piece(1, 1)
                        if event.key == pygame.K_s:
                            self.board.move_piece(4, 6)
                        if event.key == pygame.K_d:
                            self.board.move_piece(8, 1)
                        if event.key == pygame.K_f:
                            self.board.move_piece(12, 1)
                        if event.key == pygame.K_g:
                            self.board.move_piece(2, 1)
                        if event.key == pygame.K_h:
                            self.board.move_piece(3, 1)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.connection.my_player.turn_token:
                            x, y = event.pos
                            print(x, y)
                            for num in range(self.connection.my_player.low_range, self.connection.my_player.low_range + 4): #e.g for "red" - range(0, 4), for "green" - range(4, 8)
                                piece = self.connection.my_player.my_pieces[num - self.connection.my_player.low_range] #gets index 0-3 to use my_pieces.
                                pos = piece.get_position()
                                if piece.image.get_width() == 64:
                                    if pos is not None and piece.image.get_rect(topleft=(coOrds[pos][0]-7, coOrds[pos][1]-25)).collidepoint(x, y): #If you clicked a piece, move them (if you rolled)
                                        self.click_piece(num, piece)
                                        break
                                    elif piece.image.get_rect(topleft=(self.board.home_coords[num])).collidepoint(x, y) and self.connection.my_player.roll == 6: #If you clicked a piece in home and you rolled 6, move them out.
                                        self.board.move_piece(num, self.connection.my_player.roll)
                                        self.connection.send_out(num, self.connection.my_player.start)
                                        self.connection.my_player.turnstaken += 1 #Player sent piece out, increase turnstaken
                                        self.connection.my_player.roll = 0 #reset the dice so it can't be reused
                                        print("piece sent out - rolls:", self.connection.my_player.rollsleft, "-turnstaken:", self.connection.my_player.turnstaken)
                                        if self.connection.my_player.turnstaken >= 3:
                                            _thread.start_new_thread(self.connection.end_turn, ())
                                        print("Home", piece.get_steps_from_start())
                                        break
                                else:
                                    if piece.image.get_rect(topleft=(coOrds[pos][0], coOrds[pos][1])).collidepoint(x, y): #If you clicked a piece, move them (if you rolled)
                                        self.click_piece(num, piece)
                                        break
                    self.clock.tick(FPS)
            except pygame.error:
                continue

ludo = Ludo()
ludo.setup()
ludo.run()
        
##
##pygame.init()
##CLOCK = pygame.time.Clock()
##
##COLOUR_TO_IMG = {"red": RED_PIECE, "green": GREEN_PIECE, "yellow": YELLOW_PIECE, "blue": BLUE_PIECE}
##STARTING_POINT = {"red": 0, "green": 13, "yellow": 26, "blue": 39}
##CS = ["red", "green", "yellow", "blue"]
##ALL_PIECES = [Piece(CS[c], num, COLOUR_TO_IMG[CS[c]], STARTING_POINT[CS[c]]) for c in range(4) for num in range(1, 5)]
##
##genie_owner = None
##MY_PLAYER = None
##board = Board(genie_owner, MY_PLAYER, ALL_PIECES, COLOUR_TO_IMG)
##create_dicts()
###connection.my_player = Player("green", "Joe")
###connection.my_player.turn_token = True
##SCORE_BOARD = ScoreBoard()
##connection = Connection(board, MY_PLAYER, CURRENT_PLAYER, ALL_PIECES)
##board.add_connection(connection)
##connection.connect_to_server()
##
##
##def terminate():
##    pygame.quit()
##    sys.exit()
##
##def click_piece():
##    board.move_piece(num, connection.my_player.roll)
##    print("piece moved. rolls:", connection.my_player.rollsleft, "-turnstaken:", connection.my_player.turnstaken)
##    if connection.my_player.roll != 0:
##        connection.my_player.turnstaken += 1 #Player moved piece, increase turnstaken
##        print("piece moved after update rolls:", connection.my_player.rollsleft, "-turnstaken:", connection.my_player.turnstaken)
##        connection.send_movement(num, connection.my_player.roll)
##    if connection.my_player.turnstaken == 3 or connection.my_player.rollsleft == 0: #End turn if player has no rolls left, or they've already taken 3 turns.
##        _thread.start_new_thread(connection.end_turn, ()) 
##    else:
##        connection.my_player.roll = 0
##    print("Outside", piece.get_steps_from_start())
##
##def show_start_screen():
##    FPSCLOCK = pygame.time.Clock()
##    title_font = pygame.font.SysFont("Arial", 100)
##    colours = [RED, GREEN, YELLOW, BLUE]
##    index = 0
##    while True:
##        SCREEN.fill(WHITE)
##        title_surf = title_font.render('Ludo!', True, colours[index])
##        title_surf_rect = title_surf.get_rect()
##        title_surf_rect.center = (BOARD_WIDTH / 2, BOARD_HEIGHT / 2)
##        SCREEN.blit(title_surf, title_surf_rect)
##
##        if connection.my_player is not None:
##            pygame.event.get()
##            return
##        if pygame.event.get(QUIT):
##            terminate()
##        index = (index + 1) % 4
##        pygame.display.update()
##        FPSCLOCK.tick(5)
##        
##show_start_screen()
##pygame.event.set_blocked([MOUSEMOTION, KEYUP, MOUSEBUTTONUP])
##IN = 1
##while True:
##    try:
##        SCREEN.fill(WHITE)
##        SCREEN.blit(BG, (INDENT_BOARD, INDENT_BOARD))
##        board.draw_board(COLOUR_CHECK)
##        COLOUR_CHECK = (COLOUR_CHECK + 1) % FLASH_RATE
##        SCORE_BOARD.draw(ALL_PIECES)
##        board.PLAYER_FIELD.draw()
##        OUTPUT = board.ROLL_BUTTON.draw()
##        if OUTPUT is not None:
##            board.dice_object.dice.roll_dice_gif(OUTPUT, IN, 900, 230)
##        board.dice_object.display_dice(900, 230, connection.current_dice)
##        pygame.display.update()
##        for event in pygame.event.get():
##            if event.type == QUIT:
##                terminate()
##            elif event.type == pygame.KEYDOWN:
##                if event.key == pygame.K_a:
##                    board.move_piece(1, 1)
##                if event.key == pygame.K_s:
##                    board.move_piece(4, 6)
##                if event.key == pygame.K_d:
##                    board.move_piece(8, 1)
##                if event.key == pygame.K_f:
##                    board.move_piece(12, 1)
##                if event.key == pygame.K_g:
##                    board.move_piece(2, 1)
##                if event.key == pygame.K_h:
##                    board.move_piece(3, 1)
##            elif event.type == pygame.MOUSEBUTTONDOWN:
##                if connection.my_player.turn_token:
##                    x, y = event.pos
##                    print(x, y)
##                    for num in range(connection.my_player.low_range, connection.my_player.low_range + 4): #e.g for "red" - range(0, 4), for "green" - range(4, 8)
##                        piece = connection.my_player.my_pieces[num - connection.my_player.low_range] #gets index 0-3 to use my_pieces.
##                        pos = piece.get_position()
##                        if piece.image.get_width() == 64:
##                            if pos is not None and piece.image.get_rect(topleft=(coOrds[pos][0]-7, coOrds[pos][1]-25)).collidepoint(x, y): #If you clicked a piece, move them (if you rolled)
##                                click_piece()
##                                break
##                            elif piece.image.get_rect(topleft=(board.home_coords[num])).collidepoint(x, y) and connection.my_player.roll == 6: #If you clicked a piece in home and you rolled 6, move them out.
##                                board.move_piece(num, connection.my_player.roll)
##                                connection.send_out(num, connection.my_player.start)
##                                connection.my_player.turnstaken += 1 #Player sent piece out, increase turnstaken
##                                connection.my_player.roll = 0 #reset the dice so it can't be reused
##                                print("piece sent out - rolls:", connection.my_player.rollsleft, "-turnstaken:", connection.my_player.turnstaken)
##                                if connection.my_player.turnstaken >= 3:
##                                    _thread.start_new_thread(connection.end_turn, ())
##                                print("Home", piece.get_steps_from_start())
##                                break
##                        else:
##                            if piece.image.get_rect(topleft=(coOrds[pos][0], coOrds[pos][1])).collidepoint(x, y): #If you clicked a piece, move them (if you rolled)
##                                click_piece()
##                                break
##            self.clock.tick(FPS)
##    except pygame.error:
##        continue
