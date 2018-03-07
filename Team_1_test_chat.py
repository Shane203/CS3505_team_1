# Team 1
import unittest
from Team_1_chat import ChatBox
from socket import *
from tkinter import *


class TestClient(unittest.TestCase):
    def setUp(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((gethostbyname(gethostname()), 10001))
        self.chat = ChatBox(self.sock)

    def tearDown(self):
        self.sock.close()

    def test_start(self):
        name = "Team_1"
        self.chat.start(name)
        self.assertEqual(self.chat.name, name)
        self.assertIsInstance(self.chat.root, Tk)
        self.assertIsInstance(self.chat.frame, Tk)
        self.assertIsInstance(self.chat.msg, Tk)
        self.assertIsInstance(self.chat.recvd, Tk)

    def test_new_message(self):
        name = "Team_1"
        self.chat.start(name)
        txt = "hello"
        msg = {"Name": name, "msg": txt}
        self.chat.new_message(msg)
        print("end")


if __name__ == '__main__':
    unittest.main()
