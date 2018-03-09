# Team 1
import unittest
import os
import pygame
import Team_1_setup as s


class TestSetup(unittest.TestCase):
    def setUp(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pygame.quit()
        
    def test_imports(self):
        from Team_1_constants import BOX_SIZE, INDENT_BOARD

    def test_window_pos(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(0) + "," + str(25)

    def test_display(self):
        pygame.display.set_caption('Ludo Board')
        pygame.display.set_icon(pygame.image.load('images/desktop-backgrounds-30.jpg'))

    def test_dict(self):
        s.create_dicts()
        self.assertNotEqual(len(s.coOrds), 0)


if __name__ == '__main__':
    unittest.main()
