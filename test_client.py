import unittest
from client import Ludo
serv = __import__('server-1p.py')

class TestClient(unittest.TestCase):
    def setUp(self):
        serv()
        ludo = Ludo()
        ludo.setup()
        

    def test_ludo(self):
        print("hi")
        ludo.run()
        
if __name__ == '__main__':
    unittest.main()
