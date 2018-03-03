import unittest
from board import Board
from constants import *
from piece import Piece
from player import Player
from box_and_button import Box
from box_and_button import Button
from dice import Dice
from connection import Connection
import pygame
import setup as s

class TestClient(unittest.TestCase):
    def setUp(self):
        self.starting_point = {"red": 0, "green": 13, "yellow": 26, "blue": 39}
        self.cs = ["red", "green", "yellow", "blue"]
        self.colour_to_img = {"red": RED_PIECE, "green": GREEN_PIECE, "yellow": YELLOW_PIECE, "blue": BLUE_PIECE}
        self.all_pieces = [Piece(self.cs[c], num, self.colour_to_img[self.cs[c]], self.starting_point[self.cs[c]]) for c in range(4) for num in range(1, 5)]
        self.player = Player("red", "Team_1", self.all_pieces, ["a", "b", "c", "d"])
        self.board = Board(None, self.player, self.all_pieces, self.colour_to_img)
        s.create_dicts()
        
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

    def test_add_connection(self):
        self.conn = "connect"
        self.dice_object = Dice(self.conn, self.player)
        self.ROLL_BUTTON = Button("ROLL", 900, 430, 200, 30, GREEN, 0, BRIGHTGREEN, self.dice_object)
        self.current_player = self.player.colour
        self.assertIsInstance(self.dice_object, Dice)
        self.assertIsInstance(self.ROLL_BUTTON, Button)
        self.assertEqual(self.current_player, "red")

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
            self.assertEqual(moving_piece.get_position(), moving_piece.start + 1)
            

    def fake_move_piece(self, piece_num, moving_piece):
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

    def test_draw_pieces(self):
        self.board.current_player = self.player.colour
        for i in range(16):
            moving_piece = self.board.ALL_PIECES[i]
            self.assertEqual(moving_piece.image, self.colour_to_img[moving_piece.colour])
            self.assertEqual(moving_piece.image.get_width(), 64)
            if moving_piece.colour == self.board.current_player and not moving_piece.movable:
                temp = moving_piece.image
                moving_piece.image = ORANGE_PIECE_32
                self.assertEqual(moving_piece.image.get_width(), 32)
                moving_piece.image = temp

    def test_death_function(self):
        self.connection = Connection(self.board, self.player, None, self.all_pieces)
        self.board.add_connection(self.connection)
        self.board.draw_board(0)
        moving_piece = self.board.ALL_PIECES[0]
        moving_piece.set_position(10)
        moving_piece.set_steps_from_start(10)
        self.board.death_function(moving_piece)
        self.assertIsNone(moving_piece.get_position())
        self.assertEqual(moving_piece.get_steps_from_start(), 0)
        self.assertTrue(self.board.connection.my_player.specialmove)

    def test_disconnect_function(self):
        colour_list = ["red", "green", "yellow", "blue"]
        self.connection = Connection(self.board, self.player, None, self.all_pieces)
        self.board.add_connection(self.connection)
        self.board.draw_board(0)
        for colour in colour_list:
            self.board.disconnect_function(colour)
            lo = self.board.get_low_range(colour)
            for i in range(lo, lo + 4):
                piece = self.board.ALL_PIECES[i]
                self.assertEqual(piece.image, self.board.COLOUR_TO_IMG[piece.colour])
                self.assertIsNone(piece.movable)
                self.assertIsNone(piece.get_position())
                self.assertEqual(piece.get_steps_from_start(), 0)
            
    def test_get_low_range(self):
        self.assertEqual(self.board.get_low_range("red"), 0)
        self.assertEqual(self.board.get_low_range("green"), 4)
        self.assertEqual(self.board.get_low_range("yellow"), 8)
        self.assertEqual(self.board.get_low_range("blue"), 12)
                
if __name__ == '__main__':
    unittest.main()
