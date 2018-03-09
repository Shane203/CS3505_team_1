# Team 1
import unittest
from Team_1_box_and_button import *


class TestBoxAndButton(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
        
    def test_box_initialisation_without_s(self):
        self.box1 = Box("hello", 10, 100, 20, 30, 'red')
        self.assertEqual("hello", self.box1._msg)
        self.assertEqual(10, self.box1._x)
        self.assertEqual(100, self.box1._y)
        self.assertEqual(20, self.box1._w)
        self.assertEqual(30, self.box1._h)
        self.assertEqual('red', self.box1._c)
        self.assertEqual(0, self.box1._s)

    def test_set_msg(self):
        self.box = Box("hello", 10, 100, 20, 30, 'red', 2)
        self.assertEqual(self.box._msg, "hello")
        self.box.set_msg("goodbye")
        self.assertEqual(self.box._msg, "goodbye")

    def test_box_initialisation_with_size(self):
        self.box1 = Box("hello", 10, 100, 20, 30, 'red', 2)
        self.assertEqual("hello", self.box1._msg)
        self.assertEqual(10, self.box1._x)
        self.assertEqual(100, self.box1._y)
        self.assertEqual(20, self.box1._w)
        self.assertEqual(30, self.box1._h)
        self.assertEqual('red', self.box1._c)
        self.assertEqual(2, self.box1._s)

    def test_button_initialisation(self):
        self.button1 = Button("hello", 10, 100, 20, 30, 'red', 2, 'blue')
        self.assertEqual("hello", self.button1._msg)
        self.assertEqual(10, self.button1._x)
        self.assertEqual(100, self.button1._y)
        self.assertEqual(20, self.button1._w)
        self.assertEqual(30, self.button1._h)
        self.assertEqual('red', self.button1._c)
        self.assertEqual(2, self.button1._s)
        self.assertEqual('blue', self.button1._ac)

    def test_button_with_action(self):
        def func():
            return 0
        self.button1 = Button("hello", 10, 100, 20, 30, 'red', 2, 'blue', func)
        self.assertEqual("hello", self.button1._msg)
        self.assertEqual(10, self.button1._x)
        self.assertEqual(100, self.button1._y)
        self.assertEqual(20, self.button1._w)
        self.assertEqual(30, self.button1._h)
        self.assertEqual('red', self.button1._c)
        self.assertEqual(2, self.button1._s)
        self.assertEqual('blue', self.button1._ac)
        self.assertEqual(0, self.button1._action())        


if __name__ == '__main__':
    unittest.main()
