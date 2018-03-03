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

    def test_show_start_screen(self):
        self.assertIsNone(self.ludo.connection.my_player)
        screen_thread = threading.Thread(target=self.ludo.show_start_screen)
        screen_thread.start()
        self.ludo.connection.my_player = 1
        screen_thread.join()
        self.assertIsNotNone(self.ludo.connection.my_player)

    def test_score(self):
        score_list = self.ludo.get_score(self.ludo.all_pieces)
        self.assertIsInstance(score_list[0], int)
        expected_value = [0, 0, 0, 0]
        self.assertEqual(score_list, expected_value)
        piece = self.ludo.all_pieces[0]
        piece.set_steps_from_start(5)
        score_list_2 = self.ludo.get_score(self.ludo.all_pieces)
        expected_value = [5, 0, 0, 0]
        self.assertEqual(score_list_2, expected_value)
        
        
        
if __name__ == '__main__':
    unittest.main()

