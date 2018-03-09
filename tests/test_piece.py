# Team 1
import unittest
from Team_1_piece import Piece
import Team_1_constants as c
import pygame
from Team_1_player import Player


class TestPiece(unittest.TestCase):
    def setUp(self):
        self.starting_point = {"red": 0, "green": 13, "yellow": 26, "blue": 39}
        self.cs = ["red", "green", "yellow", "blue"]
        self.colour_to_img = {"red": c.RED_PIECE, "green": c.GREEN_PIECE, "yellow": c.YELLOW_PIECE,
                              "blue": c.BLUE_PIECE}
        self.all_pieces = [Piece(self.cs[c], num, self.colour_to_img[self.cs[c]], self.starting_point[self.cs[c]])
                           for c in range(4) for num in range(1, 5)]
        self.piece = self.all_pieces[0]
        
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def set_player(self):
        self.player = Player("red", "Team_1", self.all_pieces, ["a", "b", "c", "d"])
        self.piece.set_my_player(self.player)
        
    def test_initial_values(self):
        self.assertEqual(self.piece.number, 1)
        self.assertIsNone(self.piece.position, None)
        self.assertEqual(self.piece.colour, "red")
        self.assertEqual(self.piece.steps_from_start, 0)
        self.assertFalse(self.piece.movable)
        self.assertIsInstance(self.piece.image, pygame.Surface)
        self.assertEqual(self.piece.start, 0)
        self.assertIsNone(self.piece.my_player, None)
        self.assertFalse(self.piece.genie)

    def test_get_position(self):
        self.assertEqual(self.piece.position, self.piece.get_position())

    def test_set_position(self):
        self.piece.set_position(5)
        self.assertEqual(self.piece.position, 5)

    def test_get_steps_from_start(self):
        self.assertEqual(self.piece.steps_from_start, self.piece.get_steps_from_start())

    def test_set_steps_from_start(self):
        self.piece.set_steps_from_start(23)
        self.assertEqual(self.piece.steps_from_start, 23)

    def test_set_my_player(self):
        self.player = Player("red", "Team_1", self.all_pieces, ["a", "b", "c", "d"])
        self.piece.set_my_player(self.player)
        self.assertIsInstance(self.piece.my_player, Player)

    def test_check_safe_point(self):
        self.piece.set_position(8)
        self.assertTrue(self.piece.check_safe_point())
        self.piece.set_position(9)
        self.piece.set_steps_from_start(9)
        self.assertFalse(self.piece.check_safe_point())

    def test_check_home_run(self):
        self.set_player()
        self.piece.set_steps_from_start(50)
        self.piece.my_player.roll = 6
        self.assertTrue(self.piece.check_home_run())
        for i in range(51, 56):
            for roll in range(6):
                piece_pos = i + roll
                if piece_pos == 50 and roll == 6:
                    return True
                if piece_pos in range(51, 56) and (roll + piece_pos) > 55:
                    return True
                return False

    def test_check_forward_movement(self):
        self.set_player()
        for i in range(51, 56):
            for roll in range(6):
                future_pos = i + roll
                if (future_pos in range(51, 56) or future_pos > 55) and not self.piece.check_space_empty(future_pos):
                    self.assertFalse(self.piece.check_forward_movement())
                else:
                    self.assertTrue(self.piece.check_forward_movement())
            
        
if __name__ == '__main__':
    unittest.main()
