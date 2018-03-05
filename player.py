class Player(object):
    """Create an object to represent a player with 4 piece objects.
    
    The function of this class is limited to representing attributes for the player;
    therefore there are no methods. This class also holds universal attributes, like 
    all_pieces and names that are used to draw pieces and scores that don't belong to
    this client and therefore wouldn't have access to.
    
    Args:
        colour: The colour used to represent the player and all their pieces.
        name: The name displayed with this player's score and chat messages.
        all_pieces: A list of all Piece objects in the game currently.
        names: The list of all player names. Needed to display the score board.
    """
    def __init__(self, colour, name, all_pieces, names):
        self.colour = colour
        self.name = name
        # Starts off at 0. When a player moves a piece, it goes up by one.
        # When it goes up to 3, their turn automatically ends.
        self.turnstaken = 0
        # When it is their turn, it is changed to 1. It is decreased when a
        # Piece moves but it is incremented if you kill a piece/roll a 6.
        self.turn_token = False
        self.rolls_taken = 0
        self.diceroll_token = True  # Used to prevent multiple rolls a turn
        # Allows player extra dice roll after landing piece on opposing piece.
        self.special_move = False
        self.ALL_PIECES = all_pieces
        self.movable_pieces_array = []
        self.names = names
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
        self.my_pieces = []
        for piece in self.ALL_PIECES:
            if self.colour == piece.colour:
                self.my_pieces += [piece]
                piece.set_my_player(self)
        self.roll = 0
