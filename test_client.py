import unittest
import pygame
from client import Ludo
from board import Board
from piece import Piece
import threading

class TestClient(unittest.TestCase):
    def setUp(self):
        self.ludo = Ludo()
        
    def test__initial_values(self):
        self.assertEqual(self.ludo.my_player, None)
        self.assertEqual(self.ludo.genie_owner, None)
        self.assertIsInstance(self.ludo.board, Board)
        self.assertIsInstance(self.ludo.all_pieces[0], Piece)
        self.assertEqual(self.ludo.colour_check, 0)
        self.assertEqual(self.ludo.time_limited, 15)
        self.assertTrue(self.ludo.p.empty())

    def test_setup(self):
        self.ludo.setup()
        self.assertTrue(pygame.event.get_blocked(pygame.MOUSEMOTION))
        self.assertTrue(pygame.event.get_blocked(pygame.KEYUP))
        self.assertTrue(pygame.event.get_blocked(pygame.MOUSEBUTTONUP))
        self.assertEqual(self.ludo.connection, self.ludo.board.connection)

    def test_score(self):
        score_list = self.ludo.get_score(self.ludo.all_pieces)
        self.assertIsInstance(score_list[0], int)
        
if __name__ == '__main__':
    unittest.main()
