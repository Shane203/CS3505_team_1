from setup import SCREEN
import json
import pygame
import time

class Dice():
    def __init__(self, connection, my_player):
        self.connection = connection
    
    def roll_dice(self):
        if self.connection.my_player.turn_token and self.connection.my_player.roll == 0:
            msg = {"Colour": self.connection.my_player.colour, "roll": True}
            data = json.dumps(msg)
            self.connection.sock.sendall(data.encode())
            time.sleep(0.1)
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
