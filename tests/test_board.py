# Team 1
import unittest
from Team_1_board import Board
from Team_1_constants import *
from Team_1_piece import Piece
from Team_1_player import Player
from Team_1_box_and_button import Box
from Team_1_box_and_button import Button
from Team_1_dice import Dice
from Team_1_connection import Connection
import Team_1_setup as s


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.starting_point = {"red": 0, "green": 13, "yellow": 26, "blue": 39}
        self.cs = ["red", "green", "yellow", "blue"]
        self.colour_to_img = {"red": RED_PIECE, "green": GREEN_PIECE, "yellow": YELLOW_PIECE, "blue": BLUE_PIECE}
        self.all_pieces = [
            Piece(self.cs[c], num, self.colour_to_img[self.cs[c]],
                  self.starting_point[self.cs[c]])
            for c in range(4) for num in range(1, 5)]
        self.player = Player("red", "Team_1", self.all_pieces,
                             ["a", "b", "c", "d"])
        self.board = Board(self.player, self.all_pieces, self.colour_to_img)
        s.create_dicts()
        
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
        
    def test_initial_values(self):
        self.assertEqual(self.board.home_coords, [])
        self.assertEqual(self.board.my_player, self.player)
        self.assertIsNone(self.board.genie_owner)
        self.assertIsInstance(self.board.PLAYER_FIELD, Box)
        self.assertIsNone(self.board.dice_object)
        self.assertIsNone(self.board.ROLL_BUTTON)
        self.assertIsNone(self.board.connection)
        self.assertIsNone(self.board.current_player)
        self.assertIsInstance(self.board.ALL_PIECES, list)
        self.assertIsInstance(self.board.COLOUR_TO_IMG, dict)

    def test_move_piece_from_home(self):
        for i in range(16):
            moving_piece = self.board.ALL_PIECES[i]
            self.assertIsNone(moving_piece.get_position())
            self.board.move_piece(i, 1)
            self.assertEqual(moving_piece.get_position(), moving_piece.start)

    def test_move_piece_from_outside(self):
        for i in range(16):
            self.board.move_piece(i, 1)
            moving_piece = self.board.ALL_PIECES[i]
            self.fake_move_piece(i, moving_piece)
            self.assertEqual(moving_piece.get_position(),
                             moving_piece.start + 1)

    def fake_move_piece(self, piece_num, moving_piece):
        if moving_piece.get_position() == 50 and piece_num < 4:
            moving_piece.set_position(-1)
        elif moving_piece.get_position() == 11 and 8 > piece_num > 3:
            moving_piece.set_position(-11)
        elif moving_piece.get_position() == 24 and 12 > piece_num > 7:
            moving_piece.set_position(-10)
        elif moving_piece.get_position() == 37 and 16 > piece_num > 11:
            moving_piece.set_position(-20)
        elif piece_num < 8 and moving_piece.get_position() < 0:
            moving_piece.set_position(moving_piece.get_position() - 1)
        elif 7 < piece_num < 16 and moving_piece.get_position() < 0:
            moving_piece.set_position(moving_piece.get_position() + 1)
        else:
            moving_piece.set_position((moving_piece.get_position() + 1) % 52)

    def test_draw_pieces(self):
        self.board.current_player = self.player.colour
        for i in range(16):
            moving_piece = self.board.ALL_PIECES[i]
            self.assertEqual(moving_piece.image,
                             self.colour_to_img[moving_piece.colour])
            self.assertEqual(moving_piece.image.get_width(), 64)
            if moving_piece.colour == self.board.current_player and not moving_piece.movable:
                temp = moving_piece.image
                moving_piece.image = ORANGE_PIECE_32
                self.assertEqual(moving_piece.image.get_width(), 32)
                moving_piece.image = temp

    def test_disconnect_function(self):
        colour_list = ["red", "green", "yellow", "blue"]
        self.connection = Connection(self.board, self.player, None,
                                     self.all_pieces)
        self.board.add_connection(self.connection)
        self.board.draw_board(0)
        for colour in colour_list:
            self.board.disconnect_function(colour)
            lo = self.board.get_low_range(colour)
            for i in range(lo, lo + 4):
                piece = self.board.ALL_PIECES[i]
                self.assertEqual(piece.image,
                                 self.board.COLOUR_TO_IMG[piece.colour])
                self.assertIsNone(piece.movable)
                self.assertIsNone(piece.get_position())
                self.assertEqual(piece.get_steps_from_start(), 0)

    def test_get_low_range(self):
        self.assertEqual(self.board.get_low_range("red"), 0)
        self.assertEqual(self.board.get_low_range("green"), 4)
        self.assertEqual(self.board.get_low_range("yellow"), 8)
        self.assertEqual(self.board.get_low_range("blue"), 12)

    def test_score(self):
        score_list = self.board.get_score(self.all_pieces)
        self.assertIsInstance(score_list[0], int)
        expected_value = [0, 0, 0, 0]
        self.assertEqual(score_list, expected_value)
        piece = self.all_pieces[0]
        piece.set_steps_from_start(5)
        score_list_2 = self.board.get_score(self.all_pieces)
        expected_value = [5, 0, 0, 0]
        self.assertEqual(score_list_2, expected_value)


if __name__ == '__main__':
    unittest.main()
