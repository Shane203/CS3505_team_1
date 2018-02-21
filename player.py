class Player(object):
    def __init__(self, colour, name, all_pieces, names):
        self.colour = colour
        self.name = name
        # Starts off at 0. When a player moves a piece, it goes up by one.
        # When it goes up to 3, their turn automatically ends.
        self.turnstaken = 0
        # When it is their turn, it is changed to 1. It is decreased when a
        # Piece moves but it is incremented if you kill a piece/roll a 6.
        self.rollsleft = 0
        self.ALL_PIECES = all_pieces
        # Holds the list of all the players names [red_player, green_player, yellow_player, blue_player]
        self.NAMES = names
        if self.colour == "red":
            self.start = 0
            self.end = 51
            self.low_range = 0 #Is used for move_piece function
        elif self.colour == "green":
            self.start = 13
            self.end = 11
            self.low_range = 4#Is used for move_piece function
        elif self.colour == "yellow":
            self.start = 26
            self.end = 24
            self.low_range = 8#Is used for move_piece function
        elif self.colour == "blue":
            self.start = 39
            self.end = 37
            self.low_range = 12#Is used for move_piece function
        self.turn_token = False
        self.my_pieces = []
        for piece in self.ALL_PIECES:
            if self.colour == piece.colour:
                self.my_pieces += [piece]
                piece.set_my_player(self)
        self.roll = 0
