import unittest
import sys, os
from tests import test_board
from tests import test_box_and_button
from tests import test_client
from tests import test_piece
from tests import test_player
from tests import test_setup


# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

blockPrint()

# initialize the test suite
loader = unittest.TestLoader()
suite  = unittest.TestSuite()

# add tests to the test suite
suite.addTests(loader.loadTestsFromModule(test_board))
suite.addTests(loader.loadTestsFromModule(test_box_and_button))
suite.addTests(loader.loadTestsFromModule(test_client))
suite.addTests(loader.loadTestsFromModule(test_piece))
suite.addTests(loader.loadTestsFromModule(test_player))
suite.addTests(loader.loadTestsFromModule(test_setup))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
