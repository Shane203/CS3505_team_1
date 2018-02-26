import unittest
from client import Ludo

class TestClient(unittest.TestCase):
    def setUp(self):
        self.ludo = Ludo()
        
    def test__initial_values(self):
        self.assertEqual(self.ludo.my_player, None)
        self.assertEqual(self.ludo.genie_owner, None)
        
if __name__ == '__main__':
    unittest.main()
