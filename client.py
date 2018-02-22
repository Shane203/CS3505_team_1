import sys
import time
import _thread
import pygame
from piece import Piece
from player import Player
from score import ScoreBoard
import constants as c
from setup import SCREEN, create_dicts, coOrds
from board import Board
from connection import Connection
from queue import Queue

class Ludo(object):
    """This is the main Ludo class.

    It initilaises my_player, genie_owner, all_pieces, board, connection,
    the score board and the timer.

    It also holds the main run function which runs the game.
    """
    def __init__(self):
        """
        Initiliases the main attributes but does not take in any arguements.
        """
        self.my_player = None
        self.genie_owner = None
        self.starting_point = {"red": 0, "green": 13, "yellow": 26, "blue": 39}
        self.cs = ["red", "green", "yellow", "blue"]
        self.colour_to_img = {"red": c.RED_PIECE, "green": c.GREEN_PIECE, "yellow": c.YELLOW_PIECE, "blue": c.BLUE_PIECE}
        self.all_pieces = [Piece(self.cs[c], num, self.colour_to_img[self.cs[c]], self.starting_point[self.cs[c]]) for c in range(4) for num in range(1, 5)]
        self.board = Board(self.genie_owner, self.my_player, self.all_pieces, self.colour_to_img)
        self.connection = Connection(self.board, self.my_player, None, self.all_pieces)
        self.current_player = self.connection.current_player
        self.clock = pygame.time.Clock()
        self.score = ScoreBoard()
        self.IN = 1
        self.colour_check = 0
        self.time_limited = 15
        self.p = Queue()
        self.font = pygame.font.SysFont("Arial", 72)
        self.text = self.font.render("time", True, (0, 128, 0))


    def setup(self):
        """Creates the coo-rdinate dictionary for the board, initiliases
        pygame. It also blocks out some pygame events so the queue doesn't
        overflow from unneeded events such as MOUSEMOTION. It also setups
        attributes in board, connects to the server and shows the start
        screen.
        """
        create_dicts()
        pygame.init()
        pygame.event.set_blocked([pygame.MOUSEMOTION, pygame.KEYUP, pygame.MOUSEBUTTONUP])
        self.board.add_connection(self.connection)
        self.connection.connect_to_server()
        self.show_start_screen()
        self.bgm()

    def draw_Time_Out(self):  # time out function on the client side
        """Draws the timer which counts down until it reaches 0. When this
        happens it goes back to its original number and counts down again.
        """
        while True:
            j = self.time_limited + 1
            while j != 0:
                if j>6:
                    j -= 1 
                    print(str(j))
                elif j<=6:
                    pygame.mixer.Sound.play(c.noMove_sound)
                    j -= 1
                    print(str(j))
                self.p.put(str(j))
                if not self.connection.q.empty():
                    data = self.connection.q.get()  # receive a data and reset the timer
                    if data == "already push a button":
                        break
                time.sleep(1)

    def terminate(self):
        """Quit game if user closes window."""
        pygame.quit()
        sys.exit()

    def click_piece(self, num, piece):
        """
        After a dice is roller, if the player clicks a movable piece, call click_piece.
        It calls the move_piece function, it also sends what piece was moved
        to the server.
        """
        self.board.move_piece(num, self.connection.my_player.roll)
        print("piece moved. rolls:", self.connection.my_player.rollsleft, "-turnstaken:", self.connection.my_player.turnstaken)
        self.connection.my_player.turnstaken += 1 #Player moved piece, increase turnstaken
        print("piece moved after update rolls:", self.connection.my_player.rollsleft, "-turnstaken:", self.connection.my_player.turnstaken)
        self.connection.send_movement(num, self.connection.my_player.roll)
        self.connection.end_roll()
        print("Outside", piece.get_steps_from_start())

    def show_start_screen(self):
        """Shows the start screen whent game first starts.

        It shows the word LUDO in flashing colours. Once the player
        connects to the server, the screen goes away."""
        FPSCLOCK = pygame.time.Clock()
        title_font = pygame.font.SysFont("Arial", 100)
        colours = [c.RED, c.GREEN, c.YELLOW, c.BLUE]
        index = 0
        while True:
            SCREEN.fill(c.WHITE)
            title_surf = title_font.render('Ludo!', True, colours[index])
            title_surf_rect = title_surf.get_rect()
            title_surf_rect.center = (c.BOARD_WIDTH / 2, c.BOARD_HEIGHT / 2)
            SCREEN.blit(title_surf, title_surf_rect)

            if self.connection.my_player is not None:
                pygame.event.get()
                return
            if pygame.event.get(pygame.QUIT):
                self.terminate()
            index = (index + 1) % 4
            pygame.display.update()
            FPSCLOCK.tick(5)

    def run(self):
        """This is the main game method.

        It draws the board, pieces and the buttons. It also shows the dice
        rolling animation.
        """
        while True:
            try:
                SCREEN.fill(c.WHITE)
                SCREEN.blit(c.BG, (c.INDENT_BOARD, c.INDENT_BOARD))
                self.board.draw_board(self.colour_check)
                self.colour_check = (self.colour_check + 1) % c.FLASH_RATE
                self.score.draw(self.all_pieces)
                self.board.PLAYER_FIELD.draw()
                OUTPUT = self.board.ROLL_BUTTON.click()
                if OUTPUT is not None:
                    self.board.dice_object.dice.roll_dice_gif(OUTPUT, self.IN, 900, 230)
                self.board.dice_object.display_dice(900, 230, self.connection.current_dice)
                # draw remain time
                if not self.p.empty():
                    message = self.p.get()  # receive a data and reset the timer
                    if message != "time":
                        self.text = self.font.render(message, True, (0, 128, 0))
                SCREEN.blit(self.text, (900, 20))

                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
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
                        if self.connection.my_player.turn_token is True and self.connection.my_player.diceroll_token is False:
                            x, y = event.pos
                            print(x, y)
                            for num in range(self.connection.my_player.low_range, self.connection.my_player.low_range + 4): #e.g for "red" - range(0, 4), for "green" - range(4, 8)
                                piece = self.connection.my_player.my_pieces[num - self.connection.my_player.low_range] #gets index 0-3 to use my_pieces.
                                pos = piece.get_position()
                                if piece.movable:
                                    if piece.image.get_width() == 64:
                                        if pos is not None and piece.image.get_rect(topleft=(coOrds[pos][0]-7, coOrds[pos][1]-25)).collidepoint(x, y): #If you clicked a piece, move them (if you rolled)
                                            self.click_piece(num, piece)
                                            break
                                        elif piece.image.get_rect(topleft=(self.board.home_coords[num])).collidepoint(x, y) and self.connection.my_player.roll == 6: #If you clicked a piece in home and you rolled 6, move them out.
                                            self.board.move_piece(num, self.connection.my_player.roll)
                                            self.connection.send_out(num, self.connection.my_player.start)
                                            self.connection.end_roll()
                                            #print("piece sent out - rolls:", self.connection.my_player.rollsleft, "-turnstaken:", self.connection.my_player.turnstaken)
                                            print("Home", piece.get_steps_from_start())
                                            break
                                    else:
                                        if piece.image.get_rect(topleft=(coOrds[pos][0], coOrds[pos][1])).collidepoint(x, y): #If you clicked a piece, move them (if you rolled)
                                            self.click_piece(num, piece)
                                            break
                    self.clock.tick(c.FPS)
            except pygame.error:
                continue
    def bgm(self):
        pygame.mixer.pre_init(44100,16,2,4096)
        pygame.mixer.music.load("sound/BGM.mp3")
        pygame.mixer.music.play(-1)

ludo = Ludo()
ludo.setup()

try:
    _thread.start_new_thread(ludo.draw_Time_Out, ())
except:
    print("unable to start a new thread")

ludo.run()

