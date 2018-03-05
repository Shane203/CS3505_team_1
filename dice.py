from constants import SCREEN
from constants import ROLL_DICE
import json
import pygame
import time
from random import randint

class Dice():
    def __init__(self, connection, my_player):
        """Initialisation
        
        :param connection: connection to the server
        :param my_player: ?
        """
        self.connection = connection

    def dice_rule(self):
        """Checks if player can roll a dice.
        
        :var self.connection.my_player.roll: Checks previous value of dice/roll
        :var self.connection.my_player.special_move: Checks if player had its piece
        land on an opposing player's piece
        :var self.connection.my_player.rolls_taken: Counts number of rolls player
        has rolled
        :return: Player can make a legal move OR Ends turn if no legal dice
        """
        if self.connection.my_player.special_move is True and \
                self.connection.my_player.rolls_taken != 3:
            self.connection.my_player.rolls_taken += 1
            self.connection.my_player.special_move = False
            return True
        elif self.connection.my_player.rolls_taken == 0:  # Assigns First Value
            self.connection.my_player.rolls_taken = 1
            return True
        elif self.connection.my_player.rolls_taken == 1 and \
                self.connection.my_player.roll == 6:  # Assigns Second value
            self.connection.my_player.rolls_taken = 2
            return True
        elif self.connection.my_player.rolls_taken == 2 and \
                self.connection.my_player.roll == 6:  # Assigns Third value
            self.connection.my_player.rolls_taken = 3
            return True
        else:
            print("No more turns")
            self.connection.end_turn()
            return False

    def roll_dice(self):
        """If the player has the turn token, dice roll token and the player can 
        roll the dice then roll the dice.
        
        :var self.connection.my_player.turn_token: Checks if it is the player's turn.
        :var self.connection.my_player.diceroll_token: Checks if it is the 
        player's turn to roll the dice.
        :var self.dice_rule(): Returns True if the player can roll the dice.
        :var self.check_for_bias(): Introduces bias. It is more likely to roll a 6 if 
        you've no pieces on the board.
        :var self.connection.my_player.colour: The player's colour.
        """
        if self.connection.my_player.turn_token and \
                self.connection.my_player.diceroll_token and self.dice_rule():
            # Prevents roll until piece moved
            self.connection.my_player.diceroll_token = False
            bias = self.check_for_bias()
            #Constructs a msg to send to the server.
            msg = {"Colour": self.connection.my_player.colour,
                   "roll": True, "bias": bias}
            # Plays the sound for the dice roll
            pygame.mixer.Sound.play(ROLL_DICE)
            #Sends the 'msg' to the server.
            data = json.dumps(msg)
            self.connection.sock.sendall(data.encode())
            #Generates the roll dice animation.
            self.roll_dice_gif(900, 230)

    def check_for_bias(self):
        """Checks for bias in the player's pieces. This happens if the player has 
        no pieces on the board.
        
        :var self.connection.my_player.my_pieces: list of the player's pieces objects.
        :var piece.get_position(): position of piece on the board.
        :return: True if all pieces are at home (introduce bias) or False if at least 
        one piece is on the board (no bias).
        """
        for piece in self.connection.my_player.my_pieces:
            #Iterates through the player's pieces.
            if piece.get_position() is not None:
                #If at least one piece is outside/not None then return False
                return False
        #All pieces are at home.
        return True

    def roll_dice_gif(self, x, y):
        """Displays a rolling dice animation when the 'ROLL' button is pressed 
        and before the resulting dice image is displayed.
         
        :param x: x coordinate of image to be displayed in animation.
        :param y: y coordinate of image to be displayed in animation.
        """
        c = pygame.time.Clock()
        tick = 35
        i = 1
        #Turned to a string to create the images for the animation. eg. "1.gif", "2.gif".
        dice_img = 1
        while i < 15:
            if dice_img < 15:
                # ensure filename is correct
                filename = "images/" + str(dice_img) + ".gif"
                img = pygame.image.load(filename)
                img = pygame.transform.scale(img, (200, 200))
                self.display_dice(x, y, img)
                c.tick(tick)
                dice_img += 1
                #Ensures the animation looks realistic
                #Displays current dice.
                if dice_img == 14:
                    self.display_dice(x, y, self.connection.current_dice)
                    c.tick(tick)
                    dice_img = 1
            dice_rect = pygame.Rect(900, 230, 1100, 430)
            pygame.display.update(dice_rect)
            i += 1

    def display_dice(self, x, y, img):
        """Displays the dice image 'img' at position (x,y) on the SCREEN.
        
        :param x: x coordinate of dice image.
        :param y: y coorinate of dice image.
        :param img: url of the dice image
        """
        SCREEN.blit(img, (x, y))
