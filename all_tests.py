import unittest
import sys, os
import Team_1_test_board
import Team_1_test_box_and_button
import Team_1_test_chat
import Team_1_test_client
import Team_1_test_piece
import Team_1_test_player
import Team_1_test_setup


# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

blockPrint()

# initialize the test suite
loader = unittest.TestLoader()
suite  = unittest.TestSuite()

# add tests to the test suite
suite.addTests(loader.loadTestsFromModule(Team_1_test_board))
suite.addTests(loader.loadTestsFromModule(Team_1_test_box_and_button))
suite.addTests(loader.loadTestsFromModule(Team_1_test_chat))
suite.addTests(loader.loadTestsFromModule(Team_1_test_client))
suite.addTests(loader.loadTestsFromModule(Team_1_test_piece))
suite.addTests(loader.loadTestsFromModule(Team_1_test_player))
suite.addTests(loader.loadTestsFromModule(Team_1_test_setup))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
