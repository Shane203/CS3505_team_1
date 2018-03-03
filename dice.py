from constants import SCREEN
from constants import ROLL_DICE
import json
import pygame
import time
from random import randint

class Dice():
    def __init__(self, connection, my_player):
        self.connection = connection

    def dice_rule(self):
        """
        Checks if player can roll a dice
        :var self.connection.my_player.roll: Checks previous value of dice/roll
        :var self.connection.my_player.special_move: Checks if player had piece
        land on opposing player's piece
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
        if self.connection.my_player.turn_token and \
                self.connection.my_player.diceroll_token and self.dice_rule():
            # Prevents roll until piece moved
            self.connection.my_player.diceroll_token = False
            bias = self.check_for_bias()
            msg = {"Colour": self.connection.my_player.colour,
                   "roll": True, "bias": bias}
            pygame.mixer.Sound.play(ROLL_DICE)
            data = json.dumps(msg)
            self.connection.sock.sendall(data.encode())
            self.roll_dice_gif(1, 1, 900, 230)

    def check_for_bias(self):
        for piece in self.connection.my_player.my_pieces:
            if piece.get_position() is not None:
                return False
        return True

    def roll_dice_gif(self, n, in_, x, y):
        c = pygame.time.Clock()
        tick = 35
        i = 1
        while i < 15:
            if in_ < 15:
                # ensure filename is correct
                filename = "images/" + str(in_) + ".gif"
                img = pygame.image.load(filename)
                img = pygame.transform.scale(img, (200, 200))
                self.display_dice(x, y, img)
                c.tick(tick)
                in_ += 1
                if in_ == 14:
                    self.display_dice(x, y, self.connection.current_dice)
                    c.tick(tick)
                    in_ = 1
            dice_rect = pygame.Rect(900, 230, 1100, 430)
            pygame.display.update(dice_rect)
            i += 1

    def display_dice(self, x, y, img):
        SCREEN.blit(img, (x, y))
