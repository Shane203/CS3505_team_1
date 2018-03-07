from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from constants import ROLL_TO_IMG, LOW_RANGES, GENIE_BIG, LAMP_BIG, SCREEN
from random import randint
import json
import _thread
from player import Player
import time
from queue import Queue
from form import Form
from tkinter import *
from chat import ChatBox


class Connection:
    """
    Connection is used to receive all communication from the server to this
    client and vice versa. All dynamic action by client occurs through
    Connection.py.

    :param board: The board object
    :type board: instance object
    :param my_player: The player object
    :type my_player: instance object
    :param current: Current player
    :type current: str
    :param all_pieces: Array of all pieces.
    :type all_pieces: list

    """

    def __init__(self, board, my_player, current, all_pieces):
        self.sock = socket(AF_INET, SOCK_STREAM)  # Creates a TCP server socket.
        # Sets values for host- the current domain name and port number 10000.
        self.server_address = (gethostbyname(gethostname()), 10001)
        # The IP Address of the current machine.
        self.ip_addr = gethostbyname(gethostname())
        print('connecting to server at %s port %s' % self.server_address)
        print('IP address is %s' % self.ip_addr)
        self.board = board
        self.my_player = my_player
        self.current_player = current
        self.current_dice = ROLL_TO_IMG[1]
        self.ALL_PIECES = all_pieces
        self.q = Queue()
        # Creates a form object
        self.form = Form("rules.txt", self)
        self.chat = ChatBox(self.sock)
        self.roomNumber = ""
        self.colours = ["red", "green", "yellow", "blue"]

    def connection_handler(self):
        """
        This function controls all data received from the server, and updates
        the client-side program according to the received ``JSON`` messages.

        When referring to ``JSON`` message comments, if the symbols ``<>``
        are used, it implies that the data is dynamic, and what will be
        in there depends on the player colour, roll of the dice etc.

        """
        colors = ["red", "green", "yellow", "blue"]
        while True:
            data = self.sock.recv(4096).decode()  # decodes received data.
            print(data)
            msg = json.loads(data)
            # Tell the time out function to reset the time.
            self.q.put("already push a button")
            # Start implies it is the first message of the game.
            # The message comes in the form {"start":True,"colour":<colour>}
            if "start" in msg:
                names = msg["names"]
                self.my_player = Player(msg["colour"],
                                        names[colors.index(msg["colour"])],
                                        self.ALL_PIECES, names)
                self.board.my_player = self.my_player
                print(self.my_player.name, self.my_player.colour)
            # This tells all games which player's turn it is.
            # Messages come of the form {"turn_token":True,"Colour":<colour>}.
            if "turn_token" in msg:
                # If msg["Colour"] is client's colour, then it is their turn.
                if msg["colour"] == self.my_player.colour:
                    self.board.PLAYER_FIELD.set_msg("MY TURN")
                    self.my_player.turn_token = True
                    self.my_player.diceroll_token = True
                else:
                    self.board.PLAYER_FIELD.set_msg(
                        self.my_player.names[colors.index(msg[
                                                        "colour"])] + "'s turn")
                self.current_player = msg["colour"]
                self.board.current_player = msg["colour"]
            # This message is a response to pressing the "ROLL" button.
            # It comes in the form {"dicenum":<between 1-6>,"Colour":<colour>}
            if "dicenum" in msg:
                roll = msg["dicenum"]
                #  This is for the biased dice roll
                if roll > 5:
                    print("roll ===============", roll)
                    roll = 6
                self.my_player.roll = roll  # Assigned value of dice roll
                # genie_status is either "take", "return" or None
                genie_status = msg["genie_result"]
                if genie_status == "take" and self.board.genie_owner is None:
                    # If you roll to take the genie and no one currently has it
                    SCREEN.blit(GENIE_BIG, (950, 50))
                    self.board.genie_owner = msg["colour"]  # Take the genie
                    for num in range((LOW_RANGES[msg["colour"]]),
                                     (LOW_RANGES[msg["colour"]]) + 4):
                        self.ALL_PIECES[num].genie = True
                elif genie_status == "return" and \
                        self.board.genie_owner == msg["colour"]:
                    # If you roll to give back the genie and you own it
                    SCREEN.blit(LAMP_BIG, (950, 50))
                    # The genie goes back to the centre
                    self.board.genie_owner = None
                    for num in range((LOW_RANGES[msg["colour"]]),
                                     (LOW_RANGES[msg["colour"]]) + 4):
                        self.ALL_PIECES[num].genie = False
                self.current_dice = ROLL_TO_IMG[roll]  # updates the dice image.
                # If the dicenum is for this player, then react accordingly.
                if msg["colour"] == self.my_player.colour:
                    self.pieces_playable()
            # This message is broadcasted if a player moves a piece.
            # As the player moves it's own pieces, they only react to other
            if "movement" in msg and msg["colour"] != self.my_player.colour:
                # It comes in the form {"Movement":<piecenum>,
                # "Moveforward":<number-of-steps-to-move>,"colour":<colour>}
                # player's movements.
                steps = msg["steps_forward"]
                num = msg["movement"]
                self.board.move_piece(num, steps)
                if self.my_player.roll == 6:
                    self.my_player.diceroll_token = True
            if "finished" in msg and msg["colour"] != self.my_player.colour:
                self.win_condition()
            if "chat_msg" in msg:
                self.chat.new_message(msg)
            if "disconnected" in msg:
                self.board.disconnect_function(msg["colour"])

    def time_out(self):
        """
        This method is called when the timer has run out of time. It will
        automatically roll dice or move random piece when timer runs out.

        """
        if self.my_player.turn_token:
            # If able to, it will roll dice.
            if self.my_player.diceroll_token:
                self.board.dice_object.roll_dice()
                time.sleep(0.5)
            # Else, if their is a playable piece, move a random piece
            elif len(self.my_player.movable_pieces_array) != 0:
                # random_piece is value in index of movable_pieces_array
                random_piece = self.my_player.movable_pieces_array[
                    randint(0, len(self.my_player.movable_pieces_array) - 1)]
                # If random piece is not on board, move onto board
                if self.ALL_PIECES[random_piece] is None:
                    self.board.move_piece(random_piece, self.my_player.roll)
                    self.send_out(random_piece, self.my_player.start)
                    time.sleep(0.5)
                # Else move random playable piece on board.
                else:
                    self.board.move_piece(random_piece, self.my_player.roll)
                    self.send_movement(random_piece, self.my_player.roll)
                    time.sleep(0.5)
                self.end_roll()
            else:
                self.end_turn()

    def connect_to_server(self):
        """
        Connects client to server, creates thread to listen for incoming
        message.

        """
        try:
            # Tries to connect to the Server.
            _thread.start_new_thread(self.connection_handler, ())

        except ConnectionRefusedError:
            print("Error: Connection refused. Server may be "
                  "unavailable or offline.")
        except OSError:
            print("Error: Port Number may already be in use.")
        except AttributeError:
            print("Error! An error has occurred. Please try again later.")
        # Sends your name to the server.

    def send_movement(self, num, roll):
        """
         Announces to other players that one of your pieces is moving

        :param num: number of piece in ``ALL_PIECES`` array
        :type num: int
        :param roll: value of dice roll
        :type roll: int

        """
        data = {"movement": num, "steps_forward": roll,
                "colour": self.my_player.colour}
        data = json.dumps(data)
        self.sock.sendall(data.encode())

    def send_check_if_game_is_started(self, game_id):
        """
        Called when client tries to join a game. Sends message to server.

        :param game_id: the room  id of lobby game
        :type game_id: str

        """
        data = {"check_game": game_id}
        data = json.dumps(data)
        self.sock.sendall(data.encode())

    def send_join_public_game(self):
        """
        Called when user press the button "Join Public Game", informing server.

        """
        data = "show_game_list"
        data = json.dumps(data)
        self.sock.sendall(data.encode())

    def send_create_game(self, room_code):
        """
        Called when user press the button "create" during lobby, informs server.

        :param room_code: the room_code of the lobby game
        :type room_code: str

        """
        data = {"create_game": room_code}
        data = json.dumps(data)
        self.sock.sendall(data.encode())

    def send_strat_the_game(self, identification, name):
        """
        Called when client asks to start a game, sending a message to server

        :param identification: the room id of lobby game
        :type identification: str
        :param name: the name of the player
        :type name: str

        """
        data = {"start_game": True, "room_code": identification, "name": name}
        data = json.dumps(data)
        self.sock.sendall(data.encode())

    def send_join_lobby_message(self, game_id):
        """Called when user join the lobby.

        :param game_id: the game_id of the lobby game
        :type game_id: int
        """

        data = {"in_lobby": True, "game_id": int(game_id)}
        data = json.dumps(data)
        self.sock.sendall(data.encode())

    def send_leave_lobby(self, game_id):
        """Called when user leave the lobby.

        :param game_id: the game_id of the lobby game
        :type game_id: int
        """

        data = {"leave_lobby": True, "game_id": int(game_id)}
        data = json.dumps(data)
        self.sock.sendall(data.encode())

    def end_turn(self):
        """
        Called when player's turn is over. It resets player turn token, the
        amount of rolls, and ability to roll dice. Sends message to server
        informing other players your turn is over.

        """
        if self.my_player.turn_token:
            print("********************ENDTURN******************************")
            self.my_player.turn_token = False
            self.my_player.diceroll_token = False
            self.my_player.roll = 0
            self.my_player.rolls_taken = 0
            # self.my_player.turns_total = 0
            # self.my_player.rolls_total = 0
            msg = {"colour": self.my_player.colour, "turn_over": True}
            data = json.dumps(msg)
            self.sock.sendall(data.encode())

    def end_roll(self):
        """
        Called when player has finished movement of piece. Resets all player's
        ``pieces.movable`` to ``False``. Checks if player should end turn,
        Otherwise allows player another dice roll.
        Checks if all player's pieces on home run, allowing player to win.

        """
        final_pos = 0  # Check if all four pieces in home run
        first_piece = 0  # Position in index of player's first piece
        last_piece = 4
        for piece in range(first_piece, last_piece):
            self.my_player.my_pieces[piece].movable = None
            if self.my_player.my_pieces[piece].get_steps_from_start() in \
                    range(52, 56):
                final_pos += 1
                if final_pos == 4:
                    self.win_condition()
        if (self.my_player.roll != 6 or self.my_player.rolls_taken == 3) \
                and self.my_player.special_move is False:
            self.end_turn()
        else:
            self.my_player.diceroll_token = True

    def pieces_playable(self):
        """
        Checks if any or all players pieces can be played.

        :return: Array of playable pieces to be used by ``def time_out()``

        """
        flag = False  # flag: Checks if any piece movable
        self.my_player.movable_pieces_array = []
        for num in range(self.my_player.low_range,
                         self.my_player.low_range + 4):
            piece = self.my_player.my_pieces[num - self.my_player.low_range]
            piece_pos = piece.get_position()
            # Prevents piece from moving from past beyond home run and
            # prevents pieces in home run from landing on same square
            if piece.check_home_run():  # can not move
                piece.movable = False
            # Prevents piece moving onto position of another piece in home run
            elif piece.check_forward_movement() is False:
                piece.movable = False
            # Player didn't roll a six, cant move piece onto board
            elif piece_pos is None and self.my_player.roll != 6:
                piece.movable = False
            else:
                print("Highlight", piece)
                piece.movable = True
                self.my_player.movable_pieces_array.append(num)
                flag = True
        if not flag:
            self.end_turn()

    def win_condition(self):
        """
        Called when players meet's the winning conditions. Sends message
        ``"Player_Won": "my colour"`` to server and creates new thread to
        produce an end screen.

        """
        data = {"Player_Won": self.my_player.colour}
        time.sleep(0.2)
        data = json.dumps(data)
        self.sock.sendall(data.encode())
        _thread.start_new_thread(self.end_screen,
                                 (self.my_player.names,
                                  self.board.get_score(self.ALL_PIECES),
                                  "You Won!!"))

    def end_screen(self, names, scores, label):
        """
        Creates a TKinter window which shows the scores of each player
        :param names: list of player names
        :param scores: list of scores
        :param label:  text to be shown on scoreboard
        """
        player_list = []
        colours = ["red", "green", "yellow", "blue"]
        for i in range(len(names)):
            player = [names[i], scores[i], colours[i]]
            player_list += [player]
        player_list = sorted(player_list, key=lambda e: e[1], reverse=True)
        root = Tk()
        root.title("Game Finished!")
        root.configure(background='white')
        title = Label(root, height=2, bg="white", text=label)
        title.pack(padx=15, pady=20, fill=X)
        for i in range(len(player_list)):
            name = Label(root, height=2, width=8, text=player_list[i][0],
                         bg=player_list[i][2])
            name.pack(side=LEFT, padx=15, pady=20, fill=X)
            score = Label(root, height=2, width=8, text=str(player_list[i][1]),
                          bg=player_list[i][2])
            score.pack(side=RIGHT, padx=15, pady=20, fill=X)
        root.mainloop()
