from constants import SCREEN
from constants import rollDice_sound
import json
import pygame
import time
from random import randint

class Dice():
    def __init__(self, connection, my_player):
        self.connection = connection

    def dice_rule(self):
        """
        Checks which roll player is rolling and sets current roll value to dice roll
        :param dice: random int value between 1-6
        :var self.connection.my_player.roll: Checks previous value of dice/roll
        :var self.connection.my_player.specialmove: Checks if player had piece land on opposing player's piece
        :var self.connection.my_player.rollstaken: Counts number of rolls player has rolled
        :return: True = Player can make a legal move, Else(Fail-safe) = Ends turn if no legal dice
        """
        if self.connection.my_player.specialmove is True and self.connection.my_player.rollstaken != 3:
            self.connection.my_player.rollstaken += 1
            self.connection.my_player.specialmove = False
            return True
        elif self.connection.my_player.rollstaken == 0:  # Assigns First Value
            self.connection.my_player.rollstaken = 1
            return True
        elif self.connection.my_player.rollstaken == 1 and self.connection.my_player.roll == 6:  # Assigns Second value
            self.connection.my_player.rollstaken = 2
            return True
        elif self.connection.my_player.rollstaken == 2 and self.connection.my_player.roll == 6:  # Assigns Third value
            self.connection.my_player.rollstaken = 3
            return True
        else:
            print("No more turns")
            self.connection.end_turn()
            return False

    def roll_dice(self):
        if self.connection.my_player.turn_token and self.connection.my_player.diceroll_token is True and self.dice_rule() is True:
            self.connection.my_player.diceroll_token = False  # Prevents roll until piece moved
            bias = self.check_for_bias()
            msg = {"Colour": self.connection.my_player.colour, "roll": True, "bias": bias}
            pygame.mixer.Sound.play(rollDice_sound)
            data = json.dumps(msg)
            self.connection.sock.sendall(data.encode())
            #time.sleep(0.1)
            self.roll_dice_gif(1, 1, 900, 230)

    def check_for_bias(self):
        for piece in self.connection.my_player.my_pieces:
            if piece.get_position() is not None:
                return False
        return True

    def roll_dice_gif(self, n, IN, x, y):
        C = pygame.time.Clock()
        tick = 35
        i = 1
        while i < 15:
            if IN < 15:
                filename = "images/" + str(IN) + ".gif"  # ensure filename is correct
                img = pygame.image.load(filename)
                img = pygame.transform.scale(img, (200, 200))
                self.display_dice(x, y, img)
                C.tick(tick)
                IN += 1
                if IN == 14:
                    self.display_dice(x, y, self.connection.current_dice)
                    C.tick(tick)
                    IN = 1
            pygame.display.update()
            i += 1

    def display_dice(self, x, y, img):
        SCREEN.blit(img, (x, y))
