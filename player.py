class Player(object):
    """Create an object to represent a player with 4 piece objects.
    
    The function of this class is limited to representing attributes for the
    player; therefore there are no methods. This class also holds universal
    attributes, like ``all_pieces`` and ``names`` that are used to draw pieces
    and ``scores`` that don't belong to this client and therefore wouldn't have
    access to.

    :param colour: The colour used to represent player and all their pieces.
    :type colour: str
    :param name: The name displayed with player's score and chat messages.
    :type name: str
    :param all_pieces: A list of all Piece objects in the game currently.
    :type all_pieces: list
    :param names: The list of all player names. Needed to display the score
           board.
    :type names: list
    """
    def __init__(self, colour, name, all_pieces, names):
        self.colour = colour
        self.name = name
        self.ALL_PIECES = all_pieces
        self.names = names
        self.roll = 0
        self.turn_token = False  # States if it is your turn or not
        # Starts off at 0. When it goes up to 3, their turn automatically ends.
        self.rolls_taken = 0
        self.diceroll_token = True  # Used to prevent multiple rolls a turn
        # Allows player extra dice roll after landing piece on opposing piece.
        self.special_move = False
        # stores number of movable pieces
        self.movable_pieces_array = []
        self.my_pieces = []  # Stores index of my pieces
        # Sets values of piece and board positions according to your colour
        if self.colour == "red":
            self.start = 0
            self.end = 51
            self.low_range = 0  # Is used for the Board.move_piece function
        elif self.colour == "green":
            self.start = 13
            self.end = 11
            self.low_range = 4  # Is used for the Board.move_piece function
        elif self.colour == "yellow":
            self.start = 26
            self.end = 24
            self.low_range = 8  # Is used for the Board.move_piece function
        elif self.colour == "blue":
            self.start = 39
            self.end = 37
            self.low_range = 12  # Is used for the Board.move_piece function
        # Assigns pieces to player
        for piece in self.ALL_PIECES:
            if self.colour == piece.colour:
                self.my_pieces += [piece]
                piece.set_my_player(self)
