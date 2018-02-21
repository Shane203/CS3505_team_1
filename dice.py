from setup import SCREEN
import json
import pygame
import time
from random import randint

class Dice():
    def __init__(self, connection, my_player):
        self.connection = connection

    def dice_rule(self, dice):
        """
        Checks which roll player is rolling and sets current roll value to dice roll
        :param dice: random int value between 1-6
        :var MY_PLAYER.roll: Checks previous value of dice/roll
        :var MY_PLAYER.specialmove: Checks if player had piece land on opposing player's piece
        :var MY_PLAYER.rollstaken: Counts number of rolls player has rolled
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
            self.end_turn()
            return False

    def dice_roll(self):
        """
            Returns a random number between 1 and 6
        """
        return randint(1, 6)

    def roll_dice(self):
        dice = self.dice_roll()
        if self.connection.my_player.turn_token and self.connection.my_player.diceroll_token is True and self.dice_rule(dice) is True:
            self.connection.my_player.diceroll_token = False  # Prevent roll until piece moved
            self.connection.my_player.roll = dice  # Sets to dice value
            msg = {"Colour": self.connection.my_player.colour, "roll": True, "dicevalue": dice}
            data = json.dumps(msg)
            self.connection.sock.sendall(data.encode())
            #time.sleep(0.1)
            self.roll_dice_gif(1, 1, 900, 230)

    def roll_dice_gif(self, n, IN, x, y):
        C = pygame.time.Clock()
        tick = 15
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
