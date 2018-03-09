# Team 1
import sys
import time
from queue import Queue
import pygame
import _thread
from Team_1_piece import Piece
import Team_1_constants as c
from Team_1_setup import create_dicts, coOrds
from Team_1_board import Board
from Team_1_connection import Connection


class Ludo(object):
    """This is the main Ludo class.

    It initialises my_player, genie_owner, all_pieces, board, connection,
    the score board and the timer.

    It also holds the main run function which runs the game.

    :var self.my_player: Instance of Player object.
    :var self.genie_owner: Value representing owner of genie.
    :var self.starting_point: List represent starting position of each player
    :var self.colour_list: List of colours.
    :var self.colour_to_img: Image representing colour
    :var self.all_pieces: List of all pieces
    :var self.board: Instance of board object
    :var self.connection:  Instance of connection
    :var self.current_player: Current player
    :var self.colour_check: Check if flashing.
    :var self.time_limited: Amount of time before automatic movement/roll
    :var self.p: Value from server for time function to activate.
    :var self.font: Type of font
    :var self.text: Text of time function
    :type self.my_player: instance object
    :type self.genie_owner: str
    :type self.starting_point: dict
    :type self.colour_list: list
    :type self.colour_to_img: str
    :type self.all_pieces: list
    :type self.board: instance object
    :type self.connection: instance object
    :type self.current_player: str
    :type self.colour_check: str
    :type self.time_limited: int
    :type self.p: string
    :type self.font: list
    :type self.text: list
    """

    def __init__(self):
        """
        Initialises the main attributes but does not take in any arguments.
        """
        self.my_player = None
        self.genie_owner = None
        self.starting_point = {"red": 0, "green": 13, "yellow": 26, "blue": 39}
        self.colour_list = ["red", "green", "yellow", "blue"]
        self.colour_to_img = {"red": c.RED_PIECE, "green": c.GREEN_PIECE,
                              "yellow": c.YELLOW_PIECE, "blue": c.BLUE_PIECE}
        self.all_pieces = [Piece(self.colour_list[c], num,
                                 self.colour_to_img[self.colour_list[c]],
                                 self.starting_point[self.colour_list[c]])
                           for c in range(4) for num in range(1, 5)]
        self.board = Board(self.my_player,
                           self.all_pieces, self.colour_to_img)
        self.connection = Connection(self.board, self.my_player, None,
                                     self.all_pieces)
        self.current_player = self.connection.current_player
        self.clock = pygame.time.Clock()
        self.colour_check = 0
        self.time_limited = 15
        self.p = Queue()
        self.font = pygame.font.SysFont("Arial", 72)
        self.text = self.font.render("time", True, (0, 128, 0))

    def setup(self):
        """Creates the coo-rdinate dictionary for the board, initialises
        pygame. It also blocks out some pygame events so the queue doesn't
        overflow from unneeded events such as MOUSEMOTION. It also setups
        attributes in board, connects to the server and shows the start
        screen.
        """
        create_dicts()
        pygame.init()
        pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN, pygame.QUIT])
        self.board.add_connection(self.connection)
        self.connection.sock.connect(self.connection.server_address)
        self.connection.form.run()
        self.connection.connect_to_server()
        self.show_start_screen()
        self.bgm()

    def draw_time_out(self):  # time out function on the client side
        """Draws the timer which counts down until it reaches 0. When this
        happens it goes back to its original number and counts down again.
        """
        while True:
            j = self.time_limited + 1
            while j != 0:
                if j > 6:
                    j -= 1
                elif j <= 6:
                    # Show the time clock sound
                    pygame.mixer.Sound.play(c.TIMEOUT_WARNING)
                    j -= 1
                self.p.put(str(j))
                if not self.connection.q.empty():
                    data = self.connection.q.get()
                    # Receive a data and reset the timer
                    if data == "already push a button":
                        j = self.time_limited + 1
                        continue
                time.sleep(1)
            # invoke the timeout function on the connection side .
            self.connection.time_out()

    def terminate(self):
        """Quit game if user closes window."""
        pygame.quit()
        sys.exit()

    def show_start_screen(self):
        """Shows the start screen whent game first starts.

        It shows the word LUDO in flashing colours. Once the player
        connects to the server, the screen goes away.
        """
        fps_clock = pygame.time.Clock()
        title_font = pygame.font.SysFont("Arial", 100)
        colours = [c.RED, c.GREEN, c.YELLOW, c.BLUE]
        index = 0
        while True:
            c.SCREEN.fill(c.WHITE)
            title_surf = title_font.render('Ludo!', True, colours[index])
            title_surf_rect = title_surf.get_rect()
            title_surf_rect.center = (c.BOARD_WIDTH / 2, c.BOARD_HEIGHT / 2)
            c.SCREEN.blit(title_surf, title_surf_rect)

            if self.connection.my_player is not None:
                pygame.event.get()
                return
            if pygame.event.get() == pygame.QUIT:
                self.terminate()
            index = (index + 1) % 4
            pygame.display.update()
            fps_clock.tick(5)

    def bgm(self):
        """Sets the frequency, loads the background music and plays it."""
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.mixer.music.load("sound/BGM.mp3")
        pygame.mixer.music.play(-1)

    def check_click(self, x_value, y_value):
        """If there is a click after a dice has been rolled check all my_player
        pieces. If piece is movable check the size of the piece to set the
        clickable coordinates.

        :param x_value: The x_value coordinate of the click.
        :type x_value: int.
        :param y_value: The x_value coordinate of the click.
        :type y_value: int.
        """
        for num in range(self.connection.my_player.low_range,
                         self.connection.my_player.low_range + 4):
            # e.g for "red" - range(0, 4), for "green" - range(4, 8)
            piece = self.connection.my_player. \
                my_pieces[num - self.connection.my_player.low_range]
            # Gets index 0-3 to use my_pieces.
            pos = piece.get_position()
            if piece.movable:
                if piece.image.get_width() == 64:
                    # If you clicked a piece, move them (if you rolled)
                    if pos is not None and piece.image.get_rect(
                            topleft=(coOrds[pos][0] - 7,
                                     coOrds[pos][1] - 25)).collidepoint(x_value, y_value):
                        self.click_piece(num)
                        break
                    # If you clicked a piece in home and you rolled 6, move
                    # them out.
                    elif piece.image.get_rect(
                            topleft=(self.board.home_coords[num])). \
                            collidepoint(x_value, y_value) and self.connection.my_player \
                            .roll == 6:
                        self.click_piece(num)
                        break
                else:
                    # If you clicked a piece, move them (if you rolled)
                    if piece.image.get_rect(topleft=(
                            coOrds[pos][0], coOrds[pos][1])).collidepoint(x_value, y_value):
                        self.click_piece(num)
                        break

    def click_piece(self, num):
        """
        After a dice is rolled, if the player clicks a movable piece, call
        click_piece. It calls the move_piece function, it also sends what piece
        was moved to the server.

        :param num: the number of the piece.
        :type num: int.
        """
        self.board.move_piece(num, self.connection.my_player.roll)
        self.connection.send_movement(num, self.connection.my_player.roll)
        self.connection.end_roll()

    def pause(self):
        """Pauses all music and sounds."""
        pygame.mixer.music.pause()
        c.MOVE_PIECE.set_volume(0.0)
        c.ROLL_DICE.set_volume(0.0)
        c.TIMEOUT_WARNING.set_volume(0.0)
        c.KILL_PIECE.set_volume(0.0)
        return True, c.SOUND_MUTE

    def unpause(self):
        """Unpauses all music and sounds."""
        pygame.mixer.music.unpause()
        c.MOVE_PIECE.set_volume(1.0)
        c.ROLL_DICE.set_volume(1.0)
        c.TIMEOUT_WARNING.set_volume(1.0)
        c.KILL_PIECE.set_volume(1.0)
        return False, c.SOUND_OPEN

    def run(self):
        """This is the main game method.
        It draws the board, pieces and the buttons. It also shows the diceS
        rolling animation.
        """
        _thread.start_new_thread(self.connection.chat.start,
                                 (self.connection.my_player.name,))
        mute = False
        sound = c.SOUND_OPEN
        while True:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.terminate()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.connection.my_player.turn_token is True \
                                and self.connection.my_player.diceroll_token \
                                is False:
                            x_value, y_value = event.pos
                            self.check_click(x_value, y_value)
                        elif sound_icon_rect.collidepoint(event.pos) and \
                                not mute:
                            mute, sound = self.pause()
                        elif sound_icon_rect.collidepoint(event.pos) and mute:
                            mute, sound = self.unpause()
                c.SCREEN.fill(c.WHITE)  # Paint the background white.
                # Draw wooden background.
                c.SCREEN.blit(c.BG, (c.INDENT_BOARD, c.INDENT_BOARD))
                sound_icon = pygame.Surface((50, 50))
                sound_icon_rect = sound_icon.get_rect(topleft=(1100, 700))
                c.SCREEN.blit(sound, sound_icon_rect)  # Draw the sound icon.
                self.board.draw_board(self.colour_check)
                # For flashing.
                self.colour_check = (self.colour_check + 1) % c.FPS
                # Draw scoreboard
                self.board.draw_scoreboard(self.all_pieces, 900, 500, 100, 30)
                self.board.PLAYER_FIELD.draw()
                output = self.board.ROLL_BUTTON.click()
                if not self.p.empty():
                    message = self.p.get()  # receive a data and reset the timer
                    if message != "time":
                        self.text = self.font.render(message, True, (0, 128, 0))
                c.SCREEN.blit(self.text, (1100, 20))
                pygame.display.update()
                self.clock.tick(c.FPS)
            except pygame.error as error:
                print(error)
                continue


if __name__ == "__main__":
    LUDO = Ludo()
    LUDO.setup()
    try:
        _thread.start_new_thread(LUDO.draw_time_out, ())
    except OSError:
        print("Error! Server offline.")

    LUDO.run()
