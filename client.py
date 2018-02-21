import sys

import time
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
import _thread
import pygame
from piece import Piece
from pygame.locals import MOUSEMOTION, KEYUP, MOUSEBUTTONUP, QUIT
from player import Player
from constants import BOARD_WIDTH, BOARD_HEIGHT, INDENT_BOARD, BG, CURRENT_DICE
from constants import WHITE, BLACK, RED, GREEN, BLUE, YELLOW
from constants import FPS, FLASH_RATE
from constants import GENIE_BIG, LAMP_BIG, LOW_RANGES
from constants import RED_PIECE, GREEN_PIECE, YELLOW_PIECE, BLUE_PIECE
from setup import SCREEN, create_dicts, coOrds
from board import Board
from connection import Connection
from tkinter import *
from box_and_button import Box

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
        self.IN = 1
        self.colour_check = 0
        
    def setup(self):
        create_dicts()
        pygame.init()
        pygame.event.set_blocked([MOUSEMOTION, KEYUP, MOUSEBUTTONUP])
        self.board.add_connection(self.connection)
        name = self.connection.form.draw_form()
        self.connection.connect_to_server(name)
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

    def get_score(self, list_of_pieces):
        #Returns a list of the scores in order: [red, green, yellow, blue]
        red_score = 0
        blue_score = 0
        green_score = 0
        yellow_score = 0
        for piece in list_of_pieces:
            if piece.colour == "red":
                red_score += piece.get_steps_from_start()
            elif piece.colour == "blue":
                blue_score += piece.get_steps_from_start()
            elif piece.colour == "green":
                green_score += piece.get_steps_from_start()
            elif piece.colour == "yellow":
                yellow_score += piece.get_steps_from_start()
        return [red_score, green_score, yellow_score, blue_score]

    def draw_scoreboard(self, list_of_pieces):
        w = 100
        h = 30
        y = 500
        x = 900
        name = Box("Name", x, y, w, h, BLACK, 1)
        x += w
        score = Box("Score", x, y, w, h, BLACK, 1)
        x += w
        name.draw()
        score.draw()
        #Returns a list of the scores in order: red, green, yellow, blue
        scores = self.get_score(list_of_pieces)
        list_of_scores = [(scores[0], "red"), (scores[1], "green"),
                         (scores[2], "yellow"), (scores[3], "blue")]
        #If all scores are zero, scoreboard is ordered as default
        if scores != [0, 0, 0, 0]:
            list_of_scores = sorted(list_of_scores)[::-1]
        color_to_color = { "red" : RED, "green" :  GREEN, "yellow" : YELLOW, "blue" : BLUE}
        # Used to get the name of the player variable NAMES contains all the names of the
        # players [red, green, yellow, blue]
        colors = ["red", "green", "yellow", "blue"]
        for i in list_of_scores:
            #Access each player, sort them by score and draw the 4 players on the scoreboard.
            color = color_to_color[i[1]]
            y += h
            x = 900
            if self.connection.my_player.NAMES != []:
                nameField = Box( self.connection.my_player.NAMES[colors.index(i[1])],
                                 x, y, w, h, color)
            else:
                nameField = Box("", x, y, w, h, color)
            nameField.draw()
            outlineBox = Box("", x, y, w, h, BLACK, 1)
            outlineBox.draw()
            x += w
            scoreField = Box(str(i[0]), x, y, w, h, color)
            scoreField.draw()
            outlineBox = Box("", x, y, w, h, BLACK, 1)
            outlineBox.draw()
            x += w

    def run(self):
        while True:
            try:
                SCREEN.fill(WHITE)
                SCREEN.blit(BG, (INDENT_BOARD, INDENT_BOARD))
                self.board.draw_board(self.colour_check)
                self.colour_check = (self.colour_check + 1) % FLASH_RATE
                self.draw_scoreboard(self.all_pieces)
                self.board.PLAYER_FIELD.draw()
                OUTPUT = self.board.ROLL_BUTTON.click()
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
