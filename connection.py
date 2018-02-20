from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from constants import ROLL_TO_IMG, LOW_RANGES, GENIE_BIG, LAMP_BIG
from setup import SCREEN
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
                    self.my_player.rollsleft -= 1
                    if self.board.all_pool() and roll != 6:
                        self.end_turn()
                    else:
                        self.my_player.roll = roll
                        time.sleep(0.25)
                        print(roll)
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

            if msg == "time is running out" and self.my_player.turn_token == True:
                # this is the time out function
                # either randomly pick a pieces or roll a
                print("success")
                print(self.my_player.rollsleft)
                if self.my_player.rollsleft == 1:
                    self.board.dice_object.roll_dice()
                    print("here")
                    continue  # send out a message and jump to the next loop
                self.pieces_playable()
                print(len(self.my_player.movable_pieces_array))
                if len(self.my_player.movable_pieces_array) != 0:
                    i = self.my_player.movable_pieces_array[randint(0, len(self.my_player.movable_pieces_array)-1)]
                    print(i)
                    self.my_player.turnstaken +=1
                    if self.ALL_PIECES[i].position == None:
                        print("from home")
                        self.send_out(i, self.my_player.start)
                        self.my_player.roll = 0
                        self.ALL_PIECES[i].set_position(self.my_player.start)
                        self.ALL_PIECES[i].steps_from_start=0
                        print("piece sent out - rolls:", self.my_player.rollsleft, "-turnstaken:", self.my_player.turnstaken)
                        if self.my_player.turnstaken >= 3:
                            _thread.start_new_thread(self.end_turn, ())
                            print("endturn")
                    else:
                        self.board.move_piece(i,self.my_player.roll)
                        print("from board")
                        if self.my_player.roll != 0:
                            self.my_player.turnstaken +=1  # Player moved piece, increase turnstaken
                            print("piece moved after update rolls:", self.my_player.rollsleft, "-turnstaken:",
                                  self.my_player.turnstaken)
                            self.send_movement(i,self.my_player.roll)
                        if self.my_player.turnstaken == 3 or self.my_player.rollsleft == 0:  # End turn if player has no rolls left, or they've already taken 3 turns.
                            _thread.start_new_thread(self.end_turn, ())
                        else:
                            self.my_player.roll = 0
                    continue
                else:
                    _thread.start_new_thread(self.end_turn, ())

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
        """Called when player's turn is over. resets player token, rollsleft,
            turntoken."""
        if self.my_player.turn_token:
            print("********************ENDTURN******************************")
            self.my_player.turn_token = False
            self.my_player.diceroll_token = False
            self.my_player.roll = 0
            self.my_player.turnstaken = 0
            self.my_player.rollsleft = 0
            self.my_player.rollstaken = 0
            msg = {"Colour": self.my_player.colour, "turnOver": True}
            data = json.dumps(msg)
            self.sock.sendall(data.encode())

    def pieces_playable(self):
        flag = False
        self.my_player.movable_pieces_array = []
        for num in range(self.my_player.low_range, self.my_player.low_range + 4):
            piece = self.my_player.my_pieces[num - self.my_player.low_range]
            piece_pos = piece.get_position()
            if piece.check_home_run():  # Cant move
                piece.movable = False
            elif piece.check_forward_movement() is False:  # if space moving onto is not empty
                piece.movable = False
            elif piece_pos is None and self.my_player.roll != 6:  # Didn't roll a six
                piece.movable = False
            else:
                print("Highlight", piece)
                piece.movable = True
                self.my_player.movable_pieces_array.append(num)
                flag = True
        if not flag:
            self.end_turn()
            # highlight()
