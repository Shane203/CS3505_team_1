# Team 1
import unittest
from Team_1_player import Player
import Team_1_constants as c
from Team_1_piece import Piece
import pygame

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.starting_point = {"red": 0, "green": 13, "yellow": 26, "blue": 39}
        self.cs = ["red", "green", "yellow", "blue"]
        self.colour_to_img = {"red": c.RED_PIECE, "green": c.GREEN_PIECE, "yellow": c.YELLOW_PIECE,
                              "blue": c.BLUE_PIECE}
        self.all_pieces = [Piece(self.cs[c], num, self.colour_to_img[self.cs[c]], self.starting_point[self.cs[c]])
                           for c in range(4) for num in range(1, 5)]
        self.player = Player("red", "Team_1", self.all_pieces, ["a", "b", "c", "d"])

    @classmethod
    def tearDownClass(cls):
        pygame.quit()
        
    def test_initial_values(self):
        self.assertEqual(self.player.colour, "red")
        self.assertEqual(self.player.name, "Team_1")
        self.assertFalse(self.player.turn_token)
        self.assertEqual(self.player.rolls_taken, 0)
        self.assertFalse(self.player.special_move)
        self.assertTrue(self.player.diceroll_token)
        self.assertIsInstance(self.player.ALL_PIECES, list)
        self.assertEqual(len(self.player.ALL_PIECES), 16)
        self.assertEqual(len(self.player.names), 4)
        self.assertEqual(len(self.player.my_pieces), 4)
        self.assertIsInstance(self.player.my_pieces[0], Piece)
        self.assertEqual(self.player.roll, 0)

    def test_red_start_end_range(self):
        self.assertEqual(self.player.start, 0)
        self.assertEqual(self.player.end, 51)
        self.assertEqual(self.player.low_range, 0)

    def test_green_start_end_range(self):
        self.green_player = Player("green", "Team_1", self.all_pieces, ["a", "b", "c", "d"])
        self.assertEqual(self.green_player.start, 13)
        self.assertEqual(self.green_player.end, 11)
        self.assertEqual(self.green_player.low_range, 4)

    def test_yellow_start_end_range(self):
        self.yellow_player = Player("yellow", "Team_1", self.all_pieces, ["a", "b", "c", "d"])
        self.assertEqual(self.yellow_player.start, 26)
        self.assertEqual(self.yellow_player.end, 24)
        self.assertEqual(self.yellow_player.low_range, 8)

    def test_blue_start_end_range(self):
        self.blue_player = Player("blue", "Team_1", self.all_pieces, ["a", "b", "c", "d"])
        self.assertEqual(self.blue_player.start, 39)
        self.assertEqual(self.blue_player.end, 37)
        self.assertEqual(self.blue_player.low_range, 12)


if __name__ == '__main__':
    unittest.main()
