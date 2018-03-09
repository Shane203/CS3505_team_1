# Team 1
from Team_1_constants import SCREEN
from Team_1_constants import ROLL_DICE
import json
import pygame


class Dice(object):
    """
    This class controls all functionality representing the dice.

    :param connection: connection to the server
    :type connection: instance object
    """
    def __init__(self, connection):
        """Initialisation"""
        self.connection = connection

    def dice_rule(self):
        """Checks if player can roll a dice.

        If player not able to roll dice, turn is ended. Function updates amount
        of rolls taken by client.

        :return: Allow player to roll dice
        """
        # Checks if client receives extra roll by landing piece on opposing
        # player.
        if self.connection.my_player.special_move is True and \
                self.connection.my_player.rolls_taken != 3:
            self.connection.my_player.rolls_taken += 1
            self.connection.my_player.special_move = False
            return True
        # Allows client to roll a dice if this is a new turn.
        elif self.connection.my_player.rolls_taken == 0:
            self.connection.my_player.rolls_taken = 1
            return True
        # If client rolled six, allowed new dice roll.
        elif self.connection.my_player.rolls_taken == 1 and \
                self.connection.my_player.roll == 6:
            self.connection.my_player.rolls_taken = 2
            return True
        # If client rolled six, allowed new dice roll.
        elif self.connection.my_player.rolls_taken == 2 and \
                self.connection.my_player.roll == 6:
            self.connection.my_player.rolls_taken = 3
            return True
        # Else forces client to end their turn.
        else:
            self.connection.end_turn()
            return False

    def roll_dice(self):
        """Allows the client to roll the dice if the player has the turn token,
        dice roll token

        """
        if self.connection.my_player.turn_token and \
                self.connection.my_player.diceroll_token and self.dice_rule():
            # Prevents roll until piece moved
            self.connection.my_player.diceroll_token = False
            bias = self.check_for_bias()
            # Constructs a msg to send to the server.
            msg = {"colour": self.connection.my_player.colour,
                   "roll": True, "bias": bias}
            # Plays the sound for the dice roll
            pygame.mixer.Sound.play(ROLL_DICE)
            # Sends the 'msg' to the server.
            data = json.dumps(msg)
            self.connection.sock.sendall(data.encode())
            # Generates the roll dice animation.
            self.roll_dice_gif(900, 230)

    def check_for_bias(self):
        """Checks for bias in the player's pieces. This happens if the player
        has no pieces on the board.

        """
        for piece in self.connection.my_player.my_pieces:
            # Iterates through the player's pieces.
            if piece.get_position() is not None:
                # If at least one piece is outside/not None then return False
                return False
        # All pieces are at home.
        return True

    def roll_dice_gif(self, x, y):
        """Displays a rolling dice animation when the 'ROLL' button is pressed
        and before the resulting dice image is displayed.

        :param x: x coordinate of image to be displayed in animation.
        :param y: y coordinate of image to be displayed in animation.
        """
        c = pygame.time.Clock()
        tick = 20
        i = 1
        # Turned to a string to create the images for the animation.
        # eg. "1.gif", "2.gif".
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
                # Ensures the animation looks realistic
                # Displays current dice.
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
        :param y: y coordinate of dice image.
        :param img: url of the dice image
        """
        SCREEN.blit(img, (x, y))
