from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from constants import ROLL_TO_IMG, LOW_RANGES, GENIE_BIG, LAMP_BIG
from setup import SCREEN
from random import randint
import json
import pygame
import _thread
from player import Player
import time
from queue import Queue


class Connection:
    def __init__(self, board, my_player, current, all_pieces):
        self.sock = socket(AF_INET, SOCK_STREAM)  # Creates a TCP server socket.
        # Sets values for host- the current domain name and port number 10000.
        self.server_address = (gethostbyname(gethostname()), 10001)
        self.ip_addr = gethostbyname(gethostname())  # The IP Address of the current machine.
        print('connecting to server at %s port %s' % self.server_address)
        print('IP address is %s' % self.ip_addr)
        self.board = board
        self.my_player = my_player
        self.current_player = current
        self.current_dice = ROLL_TO_IMG[1]
        self.ALL_PIECES = all_pieces
        self.q = Queue()

    def connection_handler(self):
        """This function controls all data received from the server, and updates
        the client-side program accoridng to the received JSON messages.
        When referring to JSON message comments, if the symbols <> are used,
        it implies that the data is dynamic, and what will be in there depends
        on the player colour, roll of the dice etc."""
        while True:
            data = self.sock.recv(4096).decode()  # decodes received data.
            print(data)
            msg = json.loads(data)
            self.q.put("already push a button")# tell the time out function to reset the time
            # Start implies it is the first message of the game.
            # The message comes in the form {"start":True,"Colour":<colour>}
            if "start" in msg:
                self.my_player = Player(msg["Colour"], "", self.ALL_PIECES)
                self.board.my_player = self.my_player
                print(self.my_player.name, self.my_player.colour)
            # Messages come of the form {"turn_token":True,"Colour":<colour>}.
            # This tells all games which player's turn it is.
            if "turnToken" in msg:
                # If msg["Colour"] is this client's colour, then it is their turn.
                if msg["Colour"] == self.my_player.colour:
                    self.board.PLAYER_FIELD.set_msg("MY TURN")
                    self.my_player.turn_token = True
                    self.my_player.diceroll_token = True
                    self.my_player.rollsleft = 1
                    print("rolls:", self.my_player.rollsleft,
                          "-turnstaken:", self.my_player.turnstaken)
                else:
                    self.board.PLAYER_FIELD.set_msg(msg["Colour"] + "'s turn")
                self.current_player = msg["Colour"]
                self.board.current_player = msg["Colour"]
            # This message is a response to pressing the "ROLL" button.
            # It comes in the form {"dicenum":<number between 1-6>,"Colour":<colour>}
            if "dicenum" in msg:
                roll = msg["dicenum"]
                genie_status = msg["genie_result"]  # genie_status is either "take", "return" or None
                if genie_status == "take" and self.board.genie_owner is None:
                    # If you roll to take the genie and no one currently has it
                    SCREEN.blit(GENIE_BIG, (950, 50))
                    self.board.genie_owner = msg["Colour"]  # Take the genie
                    for num in range((LOW_RANGES[msg["Colour"]]), (LOW_RANGES[msg["Colour"]]) + 4):
                        self.ALL_PIECES[num].genie = True
                elif genie_status == "return" and self.board.genie_owner == msg["Colour"]:
                    # If you roll to give back the genie and you own it
                    SCREEN.blit(LAMP_BIG, (950, 50))
                    self.board.genie_owner = None  # The genie goes back to the centre
                    for num in range((LOW_RANGES[msg["Colour"]]), (LOW_RANGES[msg["Colour"]]) + 4):
                        self.ALL_PIECES[num].genie = False
                self.current_dice = ROLL_TO_IMG[roll]  # updates the dice image.
                # If the dicenum is for this player, then react accordingly.
                if msg["Colour"] == self.my_player.colour:
                    self.pieces_playable()
            # This message is broadcast by the server if a player sends out a piece from their home.
            # It comes in the form {"Sendout":<piece-number>,"pos":<startposition>}
            if "Sendout" in msg:
                piece = msg["Sendout"]
                pos = msg["pos"]
                self.ALL_PIECES[piece].set_position(pos)
                self.board.check_conflict(self.ALL_PIECES[piece])
                if roll == 6:
                    self.my_player.rollsleft += 1
            # This message is broadcast if a player moves a piece.
            # As the player moves it's own pieces, they only react to other
            if "Movement" in msg and msg["Colour"] != self.my_player.colour:
                # It comes in the form {"Movement":<piecenum>,
                # "Moveforward":<number-of-steps-to-move>,"Colour":<colour>}
                # player's movements.
                steps = msg["Moveforward"]
                num = msg["Movement"]
                self.board.move_piece(num, steps)
                if roll == 6:
                    self.my_player.rollsleft += 1
            if "Player_Won" in msg:
                print(msg)
            if msg == "time is running out" and self.my_player.turn_token == True:
                # this is the time out function
                # either randomly pick a pieces or roll a
                if self.my_player.diceroll_token:
                    self.board.dice_object.roll_dice()
                elif len(self.my_player.movable_pieces_array) != 0:  # Redundant? or fail-safe?
                    i = self.my_player.movable_pieces_array[randint(0, len(self.my_player.movable_pieces_array)-1)]
                    print("Value of I is:", i)
                    num = i.number + self.my_player.low_range - 1
                    if i.position == None:  # shouldn't it be my_pieces or i.position?
                        print("from home")
                        self.board.move_piece(num, self.my_player.roll)
                        self.send_out(num, self.my_player.start)
                        #    print("endturn")
                    else:
                        self.board.move_piece(num, self.my_player.roll)
                        print("from board")
                        self.send_movement(num, self.my_player.roll)
                    self.end_roll()
                else:
                    self.end_turn()

    def connect_to_server(self):
        try:
            # "connects Client to server, creates thread to listen for incoming messages"
            self.sock.connect(self.server_address)  # Tries to connect to the Server
            _thread.start_new_thread(self.connection_handler, ())

        except ConnectionRefusedError:
            print("Error: Connection refused. Server may be unavailable or offline.")
        except AttributeError:
            print("Error: Port Number may already be in use.")
        except AttributeError:
            print("Error! An error has occured. Please try again later.")

    def send_movement(self, num, roll):
        """Announces to other players that you are moving one of your pieces"""
        data = {"Movement": num, "Moveforward": roll, "Colour": self.my_player.colour}
        data = json.dumps(data)
        self.sock.sendall(data.encode())

    def send_out(self, num, pos):
        """Announces to other players that you are sending out one of your pieces"""
        data = {"Sendout": num, "pos": pos}
        data = json.dumps(data)
        self.sock.sendall(data.encode())

    def end_turn(self):
        """ Called when player's turn is over. Resets player values. """
        if self.my_player.turn_token:
            print("********************ENDTURN******************************")
            self.my_player.turn_token = False       # Prevent player from interacting with board
            self.my_player.diceroll_token = False   # Prevent player rolling dice
            self.my_player.roll = 0                 # Reset dice value # TODO: might be redundant
            self.my_player.rollstaken = 0           # Resets rolls taken by player
            #self.my_player.turns_total = 0     # TODO: provide total turns taken by player
            #self.my_player.rolls_total = 0     # TODO: provide total rolls taken by player
            msg = {"Colour": self.my_player.colour, "turnOver": True}
            data = json.dumps(msg)
            self.sock.sendall(data.encode())

    def end_roll(self):
        """
        Called when player has finished movement of piece.
        Resets all player's pieces.movable to FALSE.
        Checks if player should end turn, Otherwise resets diceroll_token to TRUE.
        Checks if all player's pieces on home run, allowing player to win.
        :var self.my_player.my_pieces[piece]: Players selected piece
        :var self.my_player.roll: Value of dice
        :var self.my_player.specialmove: Checks if player had piece land on opposing player's piece
        :var self.my_player.rollstaken: Counts number of rolls player has rolled this turn
        :var self.my_player.diceroll_token: Checks if player can roll allowed to roll dice
        """
        flag = 0  # flag: Counts all pieces in last four squares
        firstpiece = 0  # MY_PLAYER.lowrange  # firstpiece: First position in index of player's first piece
        lastpiece = 4  # (MY_PLAYER.lowrange + 4)
        for piece in range(firstpiece, lastpiece):
            self.my_player.my_pieces[piece].movable = None
            if self.my_player.my_pieces[piece].get_steps_from_start() in range(52, 56):  # Win Conditions
                flag += 1
                if flag == 4:
                    self.win_condition()
        if (self.my_player.roll != 6 or self.my_player.rollstaken == 3) is True and self.my_player.specialmove is False:
            self.end_turn()
        else:
            print("RESETTING DICE")
            self.my_player.diceroll_token = True

    def pieces_playable(self):
        """
        Checks if any or all pieces can be played.
        :return: Array of playable pieces
        """
        flag = False  # flag: Checks if any piece movable
        self.my_player.movable_pieces_array = []
        for num in range(self.my_player.low_range, self.my_player.low_range + 4):
            piece = self.my_player.my_pieces[num - self.my_player.low_range]
            piece_pos = piece.get_position()
            if piece.check_home_run():  # Checks if piece is on home run and can not move
                piece.movable = False
            elif piece.check_forward_movement() is False:  # Checks if space moving onto is not empty
                piece.movable = False
            elif piece_pos is None and self.my_player.roll != 6:  # Checks if piece not on board and didn't roll a six
                piece.movable = False
            else:
                print("Highlight", piece)
                piece.movable = True
                self.my_player.movable_pieces_array.append(piece)
                flag = True
        print("Number of playable pieces", len(self.my_player.movable_pieces_array))
        if not flag:
            self.end_turn()

    def win_condition(self):
        """Called when players pieces have all lined up on home run"""
        print("*****************WON THE GAME!*******************")
        time.sleep(0.1)
        data = {"Player_Won": self.my_player.colour}
        data = json.dumps(data)
        self.sock.sendall(data.encode())
        time.sleep(0.1) # Might be redundant,  need to test
        self.end_turn()