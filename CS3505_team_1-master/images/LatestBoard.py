import os
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
import json
import pygame
from pygame.locals import RESIZABLE, MOUSEMOTION, KEYUP, MOUSEBUTTONUP, QUIT
import _thread
from random import randint
# os.environ['SDL_VIDEO_CENTERED'] = '1'
os.environ['SDL_VIDEO_WINDOW_POS'] = str(0) + "," + str(25)

sock = socket(AF_INET, SOCK_STREAM)  # Creates a TCP server socket.
SERVER_ADDRESS =(gethostbyname(gethostname()), 10000)  # Sets values for host- the current domain name and port number 10000.
IPADDR = gethostbyname(gethostname())  # The IP Address of the current machine.
print('connecting to server at %s port %s' % SERVER_ADDRESS)
print('IP address is %s' % IPADDR)

def connection_handler(sock):
    """This function controls all data received from the server, and updates
    the client-side program accoridng to the received JSON messages.
    When referring to JSON message comments, if the symbols <> are used,
    it implies that the data is dynamic, and what will be in there depends
    on the player colour, roll of the dice etc."""
    while True:
        data = sock.recv(4096).decode() # decodes received data.
        print(data)
        msg = json.loads(data)
        if "start" in msg: #start implies it is the first message of the game. the message comes in the form {"start":True,"Colour":<colour>}
            global MY_PLAYER
            MY_PLAYER = Player(msg["Colour"], "")
            print(MY_PLAYER.name, MY_PLAYER.colour)
        if "turnToken" in msg: #Messages come of the form {"turn_token":True,"Colour":<colour>}. This tells all games which player's turn it is.
            if msg["Colour"] == MY_PLAYER.colour: #If msg["Colour"] is this client's colour, then it is their turn.
                PLAYER_FIELD.set_msg("MY TURN")
                MY_PLAYER.turn_token = True
                MY_PLAYER.diceroll_token = True
                MY_PLAYER.rollsleft = 1
                print("rolls:", MY_PLAYER.rollsleft, "-turnstaken:", MY_PLAYER.turnstaken)
            else:
                PLAYER_FIELD.set_msg(msg["Colour"] + "'s turn")
            global CURRENT_PLAYER
            CURRENT_PLAYER = msg["Colour"]

        if "dicenum" in msg: #This message is a response to pressing the "ROLL" button. it comes in the form {"dicenum":<number between 1-6>,"Colour":<colour>}
            roll = msg["dicenum"]
            global CURRENT_DICE
            CURRENT_DICE = ROLL_TO_IMG[roll] #updates the dice image.
            if msg["Colour"] == MY_PLAYER.colour:#If the dicenum is for this player, then react accordingly.            
                piece_playable()
        if "Sendout" in msg: #This message is broadcast by the server if a player sends out a piece from their home. it comes in the form {"Sendout":<piece-number>,"pos":<startposition>}
            piece = msg["Sendout"]
            pos = msg["pos"]
            ALL_PIECES[piece].set_position(pos)
            check_conflict(ALL_PIECES[piece])
        if "Movement" in msg and msg["Colour"] != MY_PLAYER.colour: #This message is broadcast if a player moves a piece. As the player moves it's own pieces, they only react to other
            #player's movements. It comes in the form {"Movement":<piecenum>,"Moveforward":<number-of-steps-to-move>,"Colour":<colour>}  
            steps = msg["Moveforward"]
            num = msg["Movement"]
            move_piece(num, steps)
            
def sendmovement(num, roll):
    """Announces to other players that you are moving one of your pieces"""
    #time.sleep(2)
    data = {"Movement": num, "Moveforward": roll, "Colour": MY_PLAYER.colour}
    data = json.dumps(data)
    sock.sendall(data.encode())
    
def sendout(num, pos):
    """Announces to other players that you are sending out one of your pieces"""
    data = {"Sendout": num, "pos": pos}
    data = json.dumps(data)
    sock.sendall(data.encode())
    
def end_turn():
    """Called when player's turn is over. resets player token, rollsleft, turntoken."""
    if MY_PLAYER.turn_token:
        print("********************ENDTURN******************************")
        MY_PLAYER.turn_token = False
        MY_PLAYER.diceroll_token = False
        MY_PLAYER.roll = 0
        MY_PLAYER.turnstaken = 0
        MY_PLAYER.rollsleft = 0
        MY_PLAYER.rollstaken = 0
        msg = {"Colour": MY_PLAYER.colour, "turnOver": True}
        data = json.dumps(msg)
        sock.sendall(data.encode())

def end_roll():
    """
    Called when player has finished movement of piece.
    Resets all player's pieces.movable to FALSE.
    Checks if player should end turn, Otherwise resets MY_PLAYER.diceroll_token to TRUE.
    Checks if all player's pieces on home run, allowing player to win.
    :var piece_flag: Counts all pieces in last four squares
    :var firstpiece: Position in index of player's first piece
    :var piece: Player's pieces
    :var MY_PLAYER.roll: Value of dice
    :var MY_PLAYER.specialmove: Checks if player had piece land on opposing player's piece
    :var MY_PLAYER.rollstaken: Counts number of rolls player has rolled
    :var MY_PLAYER.diceroll_token: Checks if player can roll allowed to roll dice
    :return:
    """
    piece_flag = 0
    firstpiece = 0  # MY_PLAYER.lowrange
    lastpiece = 4  # (MY_PLAYER.lowrange + 4)
    for piece in range(firstpiece, lastpiece):
        MY_PLAYER.my_pieces[piece].movable = None
        if MY_PLAYER.my_pieces[piece].get_position() in range(52, 56):  # Win Conditions
            piece_flag += 1
            if piece_flag == 4:
                won()
    if (MY_PLAYER.roll != 6 or MY_PLAYER.rollstaken == 3) is True and MY_PLAYER.specialmove is False:
        print("ROLL", MY_PLAYER.roll, MY_PLAYER.rollstaken, MY_PLAYER.specialmove)
        end_turn()
    else:
        print("RESETTING DICE")
        MY_PLAYER.diceroll_token = True

def won():
    """TODO:
        endturn()
        send msg to server to remove this player
    """
    end_turn()
    print("*****************WON THE GAME!*******************")
    data = {"Player_Won": MY_PLAYER.colour}
    data = json.dumps(data)
    sock.sendall(data.encode())

def allhome():
    for piece in MY_PLAYER.my_pieces:
        if piece.get_position() != None:
            return False
    return True

def dice_rule(dice):
    """
    TODO: MOVE to server
    Checks which roll player is rolling and sets current roll value to dice roll
    :param dice: random int value between 1-6
    :var MY_PLAYER.roll: Checks previous value of dice/roll
    :var MY_PLAYER.specialmove: Checks if player had piece land on opposing player's piece
    :var MY_PLAYER.rollstaken: Counts number of rolls player has rolled
    :return: True = Player can make a legal move, Else(Failsafe) = Ends turn if no legal dice
    """
    if MY_PLAYER.specialmove is True and MY_PLAYER.rollstaken != 3:
        MY_PLAYER.rollstaken += 1
        MY_PLAYER.specialmove = False
        return True
    elif MY_PLAYER.rollstaken == 0:  # Assigns First Value
        MY_PLAYER.rollstaken = 1
        return True
    elif MY_PLAYER.rollstaken == 1 and MY_PLAYER.roll == 6:  # Assigns Second value
        MY_PLAYER.rollstaken = 2
        return True
    elif MY_PLAYER.rollstaken == 2 and MY_PLAYER.roll == 6:  # Assigns Third value
        MY_PLAYER.rollstaken = 3
        return True
    else:
        print("No more turns")
        end_turn()
        return False

def dice_roll():

    """Returns a random number between 1 and 6
        TODO: MOVE to server
    """
    return randint(1,6)
    #return 6

def roll_dice():
    """
    TODO: MOVE to server
    Called when roll button pressed.
    Checks if dice roll allowed. Calls dice_rule to check if roll is allowed.
    :var dice: return random int value between 1-6
    :var MY_PLAYER.roll: Assigns dice value to self
    :var MY_PLAYER.turn_token: Checks if current player's turn
    :var MY_PLAYER.diceroll_token: Checks if dice roll allowed
    :return: Sends value of roll to other players, and to roll_dice_gif() to animate roll
    """
    dice = dice_roll()
    if MY_PLAYER.turn_token and MY_PLAYER.diceroll_token is True and dice_rule(dice) is True:
        MY_PLAYER.diceroll_token = False  # Prevent roll until piece moved
        MY_PLAYER.roll = dice  # Sets to dice value
        msg = {"Colour": MY_PLAYER.colour, "roll": True, "dicevalue": dice}
        data = json.dumps(msg)
        sock.sendall(data.encode())
        time.sleep(0.1)
        roll_dice_gif(dice, IN, 900, 230)

def piece_playable():
    """
    Checks if all players pieces can be moved
    :var flag: Checks if all pieces are not movable/playable. Will allow players turn to end if so.
    :return: False = Piece can not be moved, True = Piece can be moved
    """
    first_piece = MY_PLAYER.lowrange
    last_piece = (MY_PLAYER.lowrange + 4)
    flag = False
    for num in range(first_piece, last_piece):
        piece = MY_PLAYER.my_pieces[num - first_piece]
        piece_pos = piece.get_position()
        if check_home_run(piece):  # Cant move
            piece.movable = False
        elif check_forward_movement(piece) is False:  # if space moving onto is not empty
            piece.movable = False
        elif piece_pos is None and MY_PLAYER.roll != 6:  # Didn't roll a six
            piece.movable = False
        else:
            print("Highlight", piece)
            piece.movable = True
            flag = True
    if not flag:
        print("FLAG")
        end_turn()

def check_home_run(piece):
    """
    Check if piece is in home run and can be move/is playable.
    :param piece: current piece to be checked
    :return: False = Piece can't be moved, True = Piece can moved
    """
    piece_pos = piece.get_steps_from_start()
    if piece_pos == 50 and MY_PLAYER.roll == 6:
        return True
    if piece_pos in range(51, 56) and ((MY_PLAYER.roll + piece_pos) > 55):
        return True
    return False

def check_space_empty(future_pos):
    """
    Checks if the square/space, the piece is moving onto is on home run and empty.
    :param future_pos: future position of piece
    :return: False = Not empty, True = Empty
    """
    for piece in MY_PLAYER.my_pieces:
        piece_pos = piece.get_steps_from_start()
        if piece_pos in range(51, 56) and future_pos == piece_pos:  # Check if space, piece is moving onto, has piece already on it.
            return False
    return True  # Space is empty

def check_forward_movement(piece):
    """
    Check if forward position is playable/possible for this piece.
    :param piece: current piece
    :var future_pos: future position of piece = current position and dice roll
    :return: False = Piece not playable, True =
    """
    future_pos = (piece.get_steps_from_start() + MY_PLAYER.roll)
    if (future_pos in range(51, 56) or future_pos > 55) and check_space_empty(future_pos) is False:
        return False
    return True

pygame.init()

pygame.display.set_icon(pygame.image.load('desktop-backgrounds-30.jpg'))
BLUE_PIECE = pygame.image.load('blue-piece.png')
GREEN_PIECE = pygame.image.load('green-piece.png')
YELLOW_PIECE = pygame.image.load('yellow-piece.png')
RED_PIECE = pygame.image.load('red-piece.png')
ORANGE_PIECE = pygame.image.load('orange-piece.png')
ORANGE_PIECE_32 = pygame.transform.scale(ORANGE_PIECE, (32, 32))

DICE_SIZE = (200, 200)
DICE_1 = pygame.transform.scale(pygame.image.load('dice1.gif'), DICE_SIZE)
DICE_2 = pygame.transform.scale(pygame.image.load('dice2.gif'), DICE_SIZE)
DICE_3 = pygame.transform.scale(pygame.image.load('dice3.gif'), DICE_SIZE)
DICE_4 = pygame.transform.scale(pygame.image.load('dice4.gif'), DICE_SIZE)
DICE_5 = pygame.transform.scale(pygame.image.load('dice5.gif'), DICE_SIZE)
DICE_6 = pygame.transform.scale(pygame.image.load('dice6.gif'), DICE_SIZE)

ROLL_TO_IMG = {1: DICE_1, 2: DICE_2, 3: DICE_3, 4: DICE_4, 5: DICE_5, 6: DICE_6}
COLOUR_TO_IMG = {"red": RED_PIECE, "green": GREEN_PIECE, "yellow": YELLOW_PIECE, "blue": BLUE_PIECE}
CURRENT_DICE = DICE_1

BOARD_WIDTH = 1200
BOARD_HEIGHT = 800
INDENT_BOARD = 25

BOX_SIZE = 50

BG = pygame.transform.scale(pygame.image.load('wooden.jpg'), (BOX_SIZE * 15, BOX_SIZE * 15))

STAR = pygame.transform.scale(pygame.image.load('STAR.png'), (BOX_SIZE, BOX_SIZE))
UP_ARROW = pygame.transform.scale(pygame.image.load('up-arrow.png'), (BOX_SIZE, BOX_SIZE))
DOWN_ARROW = pygame.transform.scale(pygame.image.load('down-arrow.png'), (BOX_SIZE, BOX_SIZE))
LEFT_ARROW = pygame.transform.scale(pygame.image.load('left-arrow.png'), (BOX_SIZE, BOX_SIZE))
RIGHT_ARROW = pygame.transform.scale(pygame.image.load('right-arrow.png'), (BOX_SIZE, BOX_SIZE))

coOrds = dict()

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

SCREEN = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT), RESIZABLE)
pygame.display.set_caption('Ludo Board')

FPS = 10
CLOCK = pygame.time.Clock()
class Box(object):
    def __init__(self, msg, x, y, w, h, c, s):
        self._msg = msg
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._c = c
        self._s = s

    def set_msg(self, msg):
        self._msg = msg

    def draw(self):
        pygame.draw.rect(SCREEN, self._c, (self._x, self._y, self._w, self._h), self._s)
        small_text = pygame.font.Font("freesansbold.ttf", 20)
        text_surf, text_rect = text_objects(self._msg, small_text)
        text_rect.center = ((self._x + (self._w/2)), (self._y+(self._h/2)))
        SCREEN.blit(text_surf, text_rect)

class Button(Box):
    def __init__(self, msg, x, y, w, h, c, s, ac, action=None):
        Box.__init__(self, msg, x, y, w, h, c, s)
        self._ac = ac
        self._action = action

    def draw(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self._x + self._w > mouse[0] > self._x and self._y + self._h > mouse[1] > self._y:
            pygame.draw.rect(SCREEN, self._ac, (self._x, self._y, self._w, self._h), self._s)
            if click[0] == 1 and self._action != None:
                return self._action()
        else:
            pygame.draw.rect(SCREEN, self._c, (self._x, self._y, self._w, self._h), self._s)
        small_text = pygame.font.Font("freesansbold.ttf", 20)
        text_surf, text_rect = text_objects(self._msg, small_text)
        text_rect.center = ((self._x + (self._w/2)), (self._y+(self._h/2)))
        SCREEN.blit(text_surf, text_rect)
        return None

class ScoreBoard():
    def __init__(self):
        self._rows = 1
        self._cols = 2

    def draw(self, list_of_pieces):
        w = 100
        h = 30
        y = 500
        x = 900
        red_score = 0
        blue_score = 0
        green_score = 0
        yellow_score = 0
        color = Box("Color", x, y, w, h, BLACK, 1)
        x += w
        score = Box("Score", x, y, w, h, BLACK, 1)
        x += w
        color.draw()
        score.draw()
        for piece in list_of_pieces:
            if piece.colour == "red":
                red_score += piece.get_steps_from_start()
            elif piece.colour == "blue":
                blue_score += piece.get_steps_from_start()
            elif piece.colour == "green":
                green_score += piece.get_steps_from_start()
            elif piece.colour == "yellow":
                yellow_score += piece.get_steps_from_start()

        list_of_scores = [(red_score, "red"), (blue_score, "blue"),
                          (green_score, "green"), (yellow_score, "yellow")]
        list_of_scores = sorted(list_of_scores)[::-1]
        for i in list_of_scores:
            #Access each player, sort them by score and draw the 4 players on the scoreboard.
            y += h
            x = 900
            color_field = Box(i[1], x, y, w, h, BLACK, 1)
            color_field.draw()
            x += w
            score_field = Box(str(i[0]), x, y, w, h, BLACK, 1)
            score_field.draw()
            x += w

def roll_dice_gif(n, IN, x, y):
    C = pygame.time.Clock()
    tick = 15
    i = 1
    while i < 15:
        if IN < 15:
            filename = str(IN) + ".gif"  # ensure filename is correct
            img = pygame.image.load(filename)
            img = pygame.transform.scale(img, (200, 200))
            display_dice(x, y, img)
            c.tick(tick)
            IN += 1
            if IN == 14:
                display_dice(x, y, CURRENT_DICE)
                C.tick(tick)
                IN = 1
        pygame.display.update()
        i += 1

def text_objects(text, font):
    text_surface = font.render(text, True, BLACK)
    return text_surface, text_surface.get_rect()

def display_dice(x, y, img):
    SCREEN.blit(img, (x, y))
    
class Piece(object):
    def __init__(self, colour, number, position):
        self.number = number
        self.position = position
        self.colour = colour
        self.steps_from_start = 0
        self.movable = False
        if self.colour == "red":
            self.image = RED_PIECE
            self.start = 0
        elif self.colour == "green":
            self.image = GREEN_PIECE
            self.start = 13
        elif self.colour == "yellow":
            self.image = YELLOW_PIECE
            self.start = 26
        elif self.colour == "blue":
            self.image = BLUE_PIECE
            self.start = 39

    def __str__(self):
        string = "(%s-%d-%s)" % (self.colour, self.number, self.position)
        return string

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    def get_steps_from_start(self):
        return self.steps_from_start

    def set_steps_from_start(self, steps):
        self.steps_from_start = steps

class Player(object):
    def __init__(self, colour, name):
        self.colour = colour
        self.name = name
        self.diceroll_token = True
        self.specialmove = False  # Allows player to roll dice after landing piece on opposing players piece.
        self.turnstaken = 0 #starts off at 0. When a player moves a piece, it goes up by one. When it goes up to 3, their turn automatically ends.
        self.rollstaken = 0 #When it is their turn, it is changed to 1. It is decreased when a piece moves, but it is incremented if you kill a piece/roll a 6.
        if self.colour == "red":
            self.start = 0
            self.end = 51
            self.lowrange = 0 #Is used for move_piece function
        elif self.colour == "green":
            self.start = 13
            self.end = 11
            self.lowrange = 4#Is used for move_piece function
        elif self.colour == "yellow":
            self.start = 26
            self.end = 24
            self.lowrange = 8#Is used for move_piece function
        elif self.colour == "blue":
            self.start = 39
            self.end = 37
            self.lowrange = 12#Is used for move_piece function
        self.turn_token = False
        self.my_pieces = []
        for piece in ALL_PIECES:
            if self.colour == piece.colour:
                self.my_pieces += [piece]
        self.roll = 0

    def get_score(self):
        add = 0
        for num in range(4):
            if self.my_pieces[num].get_position() is None:
                continue
            if self.my_pieces[num].get_position() < 0:
                add += ALL_PIECES[num].get_steps_from_start()
                add += 11
            else:
                add += ALL_PIECES[num].get_steps_from_start() + 1
                
c = pygame.time.Clock()
def move_piece(piece_num, step):
    moving_piece = ALL_PIECES[piece_num]
    if moving_piece.get_position() is None:
        moving_piece.set_position(moving_piece.start)
    else:
        moving_piece.steps_from_start += step
        while step > 0:
            if moving_piece.get_position() == 50 and piece_num < 4:
                moving_piece.set_position(-1)
            elif moving_piece.get_position() == 11 and 8 > piece_num > 3:
                moving_piece.set_position(-11)
            elif moving_piece.get_position() == 24 and 12 > piece_num > 7:
                moving_piece.set_position(-10)
            elif moving_piece.get_position() == 37 and 16 > piece_num > 11:
                moving_piece.set_position(-20)
            elif piece_num < 8  and moving_piece.get_position() < 0:
                moving_piece.set_position(moving_piece.get_position() -1)
            elif 7 < piece_num < 16 and moving_piece.get_position() < 0:
                moving_piece.set_position(moving_piece.get_position() + 1)
            else:
                moving_piece.set_position((moving_piece.get_position()+1)%52)
            step -= 1
            draw_pieces(home_coords)
            pygame.display.update()
            c.tick(10)
    check_conflict(moving_piece)

def check_conflict(moving_piece):
    for piece in ALL_PIECES:
        equal_pos = moving_piece.get_position() == piece.get_position()
        equal_colour = moving_piece.colour != piece.colour
        if equal_pos and equal_colour and not moving_piece.get_position() == moving_piece.start:
            if not check_safe_point(piece):
                death_function(piece)
                check_many_pieces(piece)
                check_many_pieces(moving_piece)
                break
        check_many_pieces(piece)

def check_many_pieces(moving_piece):
    for num in range(16):
        piece = ALL_PIECES[num]
        if piece == moving_piece:
            continue
        if moving_piece.get_position() is not None and moving_piece.get_position() == piece.get_position():
            piece.image = pygame.transform.scale(piece.image, (32, 32))
            moving_piece.image = pygame.transform.scale(moving_piece.image, (32, 32))
            return
    moving_piece.image = COLOUR_TO_IMG[moving_piece.colour]

def check_safe_point(piece):
    if piece.get_position() in [8, 21, 34, 47]:
        return True
    elif piece.get_position() is not None and piece.get_steps_from_start() == 0:
        return True
    return False

def death_function(piece):
    piece.set_position(piece.get_position() - 1)
    check_conflict(piece)
    while piece.get_position() != piece.start:
        piece.set_position(piece.get_position() - 1)
        if piece.get_position() == -1:
            piece.set_position(51)
        draw_pieces(home_coords)
        pygame.display.update()
        c.tick(10)
    piece.set_position(None)
    piece.set_steps_from_start(0)
    MY_PLAYER.specialmove = True  # Allows roll if player's piece lands on opposing piece

def create_dicts():
    lst = [[51, 0, 1, 2, 3, 4, 18, 19, 20, 21, 22, 23],
           [50, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10, 24],
           [49, 48, 47, 46, 45, 44, 30, 29, 28, 27, 26, 25]]
    lst2 = [[10, 9, 8, 7, 6, 5, 43, 42, 41, 40, 39, 38],
            [11, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, 37],
            [12, 13, 14, 15, 16, 17, 31, 32, 33, 34, 35, 36]]
    start_y = BOX_SIZE * 5 + INDENT_BOARD
    for i in range(3):
        start_x = INDENT_BOARD
        start_y += BOX_SIZE
        for j in range(12):
            coOrds[lst[i][j]] = (start_x, start_y)
            coOrds[lst2[i][j]] = (start_y, start_x)
            start_x += BOX_SIZE
            if j == 5:
                start_x += BOX_SIZE * 3

def draw_boxes():
    box_pos = [[0, -1, -2, -3, -4, -5], [-11, -12, -13, -14, -15, 13], [-6, -7, -8, -9, -10, 26], [39, -16, -17, -18, -19, -20],
              [51, 1, 2, 3, 4, 18, 19, 20, 21, 22, 23, 50, 24, 49, 48, 47, 46, 45, 44, 30, 29, 28, 27, 26, 25,
               11, 10, 9, 8, 7, 6, 5, 43, 42, 41, 40, 38, 37, 12, 14, 15, 16, 17, 31, 32, 33, 34, 35, 36],
              [8, 34, 21, 47]]
    for item in box_pos[0]:
        pygame.draw.rect(SCREEN, RED, (coOrds[item][0], coOrds[item][1], BOX_SIZE, BOX_SIZE), 0)
        pygame.draw.rect(SCREEN, BLACK, (coOrds[item][0], coOrds[item][1], BOX_SIZE, BOX_SIZE), 1)
    for item in box_pos[1]:
        pygame.draw.rect(SCREEN, GREEN, (coOrds[item][0], coOrds[item][1], BOX_SIZE, BOX_SIZE), 0)
        pygame.draw.rect(SCREEN, BLACK, (coOrds[item][0], coOrds[item][1], BOX_SIZE, BOX_SIZE), 1)
    for item in box_pos[2]:
        pygame.draw.rect(SCREEN, YELLOW, (coOrds[item][0], coOrds[item][1], BOX_SIZE, BOX_SIZE), 0)
        pygame.draw.rect(SCREEN, BLACK, (coOrds[item][0], coOrds[item][1], BOX_SIZE, BOX_SIZE), 1)
    for item in box_pos[3]:
        pygame.draw.rect(SCREEN, BLUE, (coOrds[item][0], coOrds[item][1], BOX_SIZE, BOX_SIZE), 0)
        pygame.draw.rect(SCREEN, BLACK, (coOrds[item][0], coOrds[item][1], BOX_SIZE, BOX_SIZE), 1)
    for item in box_pos[4]:
        pygame.draw.rect(SCREEN, BLACK,(coOrds[item][0], coOrds[item][1], BOX_SIZE, BOX_SIZE), 1)
    for item in box_pos[5]:
        SCREEN.blit(STAR, (coOrds[item][0], coOrds[item][1]))

def draw_pieces(home_coords, check=0):
    piece_in = {}
    temp = None
    for num in range(16):
        piece = ALL_PIECES[num]
        piece_pos = piece.get_position()
        if piece.colour == CURRENT_PLAYER and piece.movable and check > FPS * 2:
            temp = piece.image
            if piece.image.get_width() != 64:
                piece.image = ORANGE_PIECE_32
            else:
                piece.image = ORANGE_PIECE
        if piece_pos is None:
            SCREEN.blit(piece.image, home_coords[num])
        else:
            if piece.image.get_width() != 64:
                if piece.get_position() not in piece_in:
                    piece_in[piece.get_position()] = 0
                    SCREEN.blit(piece.image, (coOrds[piece_pos][0], coOrds[piece_pos][1]))
                    piece_in[piece.get_position()] += 1
                elif piece_in[piece.get_position()] == 1:
                    SCREEN.blit(piece.image, (coOrds[piece_pos][0] + 20, coOrds[piece_pos][1]))
                    piece_in[piece.get_position()] += 1
                else:
                    SCREEN.blit(piece.image, (coOrds[piece_pos][0] + 10, coOrds[piece_pos][1] + 15))
            else:
                SCREEN.blit(piece.image, (coOrds[piece_pos][0] - 7, coOrds[piece_pos][1] - 25))
        if temp:
            piece.image = temp
            temp = None

def draw_board(home_coords, check):
    colours = [RED, GREEN, YELLOW, BLUE]

    top_left_x = BOX_SIZE * 6 + INDENT_BOARD
    top_left_y = BOX_SIZE * 6 + INDENT_BOARD
    centre = (BOX_SIZE * 7.5 + INDENT_BOARD, BOX_SIZE * 7.5 + INDENT_BOARD)
    top_left = (top_left_x, top_left_y)
    bottom_left = (top_left_x, top_left_y + BOX_SIZE * 3)
    bottom_right = (top_left_x + BOX_SIZE * 3, top_left_y + BOX_SIZE * 3)
    top_right = (top_left_x + BOX_SIZE * 3, top_left_y)

    pygame.draw.polygon(SCREEN, RED, (centre, top_left, bottom_left), 0)
    pygame.draw.polygon(SCREEN, GREEN, (centre, top_left, top_right), 0)
    pygame.draw.polygon(SCREEN, YELLOW, (centre, top_right, bottom_right), 0)
    pygame.draw.polygon(SCREEN, BLUE, (centre, bottom_left, bottom_right), 0)
    pygame.draw.polygon(SCREEN, BLACK, (centre, top_left, bottom_left), 1)
    pygame.draw.polygon(SCREEN, BLACK, (centre, top_left, top_right), 1)
    pygame.draw.polygon(SCREEN, BLACK, (centre, top_right, bottom_right), 1)
    pygame.draw.polygon(SCREEN, BLACK, (centre, bottom_left, bottom_right), 1)

    draw_boxes()

    #Print Arrows on SCREEN
    SCREEN.blit(UP_ARROW, (BOX_SIZE * 7 + INDENT_BOARD, BOX_SIZE * 14 + INDENT_BOARD))
    SCREEN.blit(DOWN_ARROW, (BOX_SIZE * 7 + INDENT_BOARD, INDENT_BOARD))
    SCREEN.blit(RIGHT_ARROW, (INDENT_BOARD, BOX_SIZE * 7 + INDENT_BOARD))
    SCREEN.blit(LEFT_ARROW, (BOX_SIZE * 14 + INDENT_BOARD, BOX_SIZE * 7 + INDENT_BOARD))
    
    #Drawing home bases and each players pieces
    home = [(INDENT_BOARD, INDENT_BOARD), (BOX_SIZE * 9 + INDENT_BOARD, INDENT_BOARD), (BOX_SIZE * 9 + INDENT_BOARD, BOX_SIZE * 9 + INDENT_BOARD), (INDENT_BOARD, BOX_SIZE * 9 + INDENT_BOARD)]
    radius = 28
    home_size = BOX_SIZE * 6
    for i in range(4):
        white_box_x = home[i][0] + BOX_SIZE
        white_box_y = home[i][1] + BOX_SIZE
        white_box = BOX_SIZE * 4
        if CURRENT_PLAYER == "red" and colours[i] == RED and check > FPS * 6:
            pygame.draw.rect(SCREEN, ORANGE, (home[i][0], home[i][1], home_size, home_size))
        elif CURRENT_PLAYER == "green" and colours[i] == GREEN and check > FPS * 6:
            pygame.draw.rect(SCREEN, LGREEN, (home[i][0], home[i][1], home_size, home_size))
        elif CURRENT_PLAYER == "yellow" and colours[i] == YELLOW and check > FPS * 6:
            pygame.draw.rect(SCREEN, LYELLOW, (home[i][0], home[i][1], home_size, home_size))
        elif CURRENT_PLAYER == "blue" and colours[i] == BLUE and check > FPS * 6:
            pygame.draw.rect(SCREEN, LBLUE, (home[i][0], home[i][1], home_size, home_size))
        else:
            pygame.draw.rect(SCREEN, colours[i], (home[i][0], home[i][1], home_size, home_size))
        pygame.draw.rect(SCREEN, BLACK, (home[i][0], home[i][1], home_size, home_size), 1)
        pygame.draw.rect(SCREEN, WHITE, (white_box_x, white_box_y, white_box, white_box))
        pygame.draw.rect(SCREEN, BLACK, (white_box_x, white_box_y, white_box, white_box), 1)

        circle_1x = white_box_x + BOX_SIZE
        circle_1y = white_box_y + BOX_SIZE
        circle_2x = white_box_x + (BOX_SIZE * 3)
        circle_2y = white_box_y + (BOX_SIZE * 3)

        pygame.draw.circle(SCREEN, colours[i], (circle_1x, circle_1y), radius, 0)
        pygame.draw.circle(SCREEN, BLACK, (circle_1x, circle_1y), radius, 1)
        
        pygame.draw.circle(SCREEN, colours[i], (circle_2x, circle_1y), radius, 0)
        pygame.draw.circle(SCREEN, BLACK, (circle_2x, circle_1y), radius, 1)
        
        pygame.draw.circle(SCREEN, colours[i], (circle_1x, circle_2y), radius, 0)
        pygame.draw.circle(SCREEN, BLACK, (circle_1x, circle_2y), radius, 1)
        
        pygame.draw.circle(SCREEN, colours[i], (circle_2x, circle_2y), radius, 0)
        pygame.draw.circle(SCREEN, BLACK, (circle_2x, circle_2y), radius, 1)
        if len(home_coords) < 15:
            home_coords += [(circle_1x - 32, circle_1y - 64), (circle_2x - 32, circle_1y - 64),
                            (circle_1x - 32, circle_2y - 64), (circle_2x - 32, circle_2y - 64)]
    draw_pieces(home_coords, check)
    PLAYER_FIELD.draw()
    display_dice(900, 230, CURRENT_DICE)
    ROLL_BUTTON.draw()

CS = ["red", "green", "yellow", "blue"]
ALL_PIECES = [Piece(CS[c], num, None) for c in range(4) for num in range(1, 5)]

create_dicts()
POS = dict([(v, k) for k, v in coOrds.items()])
home_coords = []

MY_PLAYER = None
#MY_PLAYER = Player("green", "Joe")
#MY_PLAYER.turn_token = True
CURRENT_PLAYER = None
PLAYER_FIELD = Box("", 900, 200, 200, 30, WHITE, 1)
ROLL_BUTTON = Button("ROLL", 900, 430, 200, 30, GREEN, 0, BRIGHTGREEN, roll_dice)
SCORE_BOARD = ScoreBoard()

try:
#"connects Client to server, creates thread to listen for incoming messages"
    sock.connect(SERVER_ADDRESS) # Tries to connect to the Server
    _thread.start_new_thread ( connection_handler, (sock,) )
    
except ConnectionRefusedError:
        print("Error: Connection refused. Server may be unavailable or offline.")
except AttributeError:
    print("Error: Port Number may already be in use.")
except AttributeError:
    print("Error! An error has occured. Please try again later.")

def terminate():
    pygame.quit()
    sys.exit()
    
def show_start_screen():
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

        if MY_PLAYER is not None:
            pygame.event.get()
            return
        if pygame.event.get(QUIT):
            terminate()
        index += 1
        index %= 4
        pygame.display.update()
        FPSCLOCK.tick(5)
        
show_start_screen()
COLOUR_CHECK = 0
FLASH_RATE = FPS * 8
pygame.event.set_blocked([MOUSEMOTION, KEYUP, MOUSEBUTTONUP])
IN = 1
while True:
    try:
        SCREEN.fill(WHITE)
        SCREEN.blit(BG, (INDENT_BOARD, INDENT_BOARD))
        draw_board(home_coords, COLOUR_CHECK)
        COLOUR_CHECK += 1
        COLOUR_CHECK %= FLASH_RATE
        SCORE_BOARD.draw(ALL_PIECES)
        PLAYER_FIELD.draw()
        OUTPUT = ROLL_BUTTON.draw()
        if OUTPUT is not None:
            roll_dice_gif(OUTPUT, IN, 900, 230)
        display_dice(900, 230, CURRENT_DICE)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    move_piece(1, 1)
                if event.key == pygame.K_s:
                    move_piece(4, 6)
                if event.key == pygame.K_d:
                    move_piece(8, 1)
                if event.key == pygame.K_f:
                    move_piece(12, 1)
                if event.key == pygame.K_g:
                    move_piece(2, 1)
                if event.key == pygame.K_h:
                    move_piece(3, 1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if MY_PLAYER.turn_token and MY_PLAYER.diceroll_token is False:
                    x, y = event.pos
                    print(x, y)
                    for num in range(MY_PLAYER.lowrange, MY_PLAYER.lowrange + 4):  # e.g for "red" - range(0, 4), for "green" - range(4, 8)
                        piece = MY_PLAYER.my_pieces[num - MY_PLAYER.lowrange]  # gets index 0-3 to use my_pieces.
                        pos = piece.get_position()
                        if piece.movable:  # Check if piece movable
                            if piece.image.get_width() == 64:
                                if pos is not None and piece.image.get_rect(topleft=(coOrds[pos][0]-7, coOrds[pos][1]-25)).collidepoint(x, y):  # If you clicked a piece, move them (if you rolled)
                                    move_piece(num, MY_PLAYER.roll)
                                    sendmovement(num, MY_PLAYER.roll)
                                    end_roll()  # Checks if players turn is over
                                elif piece.image.get_rect(topleft=(home_coords[num])).collidepoint(x, y) and MY_PLAYER.roll == 6:  # If you clicked a piece in home and you rolled 6, move them out.
                                    move_piece(num, MY_PLAYER.roll)
                                    sendout(num, MY_PLAYER.start)
                                    end_roll()  # Checks if players turn is over
                            elif piece.image.get_rect(topleft=(coOrds[pos][0], coOrds[pos][1])).collidepoint(x, y):  # If you clicked a piece, move them (if you rolled)
                                    move_piece(num, MY_PLAYER.roll)
                                    sendmovement(num, MY_PLAYER.roll)
                                    end_roll()  # Checks if players turn is over
            CLOCK.tick(FPS)
    except pygame.error:
        print("ERROR OCCURRED IN LOOP", pygame.get_error())
        continue
