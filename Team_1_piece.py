# Team 1
class Piece(object):
    """Creates the piece objects that move around the board.

    It also prints the piece attributes, gets and sets piece position, gets
    and sets piece steps_from_start. It also does checks to make sure if the
    piece movement is legal or not.

    :param colour: The colour of the piece.
    :param number: The number of the piece.
    :param image: The image the piece shows on the board.
    :param start: The piece's starting position.
    """
    def __init__(self, colour, number, image, start):
        self.number = number
        self.position = None
        self.colour = colour
        self.steps_from_start = 0
        self.movable = False
        self.image = image
        self.start = start
        self.my_player = None
        self.genie = False

    def __str__(self):
        """Prints the piece colour, number and position."""
        string = "(%s-%d-%s)" % (self.colour, self.number, self.position)
        return string

    def get_position(self):
        """Returns the position of the piece."""
        return self.position

    def set_position(self, position):
        """Sets the position of the piece."""
        self.position = position

    def get_steps_from_start(self):
        """Returns the steps from starting position of the piece."""
        return self.steps_from_start

    def set_steps_from_start(self, steps):
        """Sets the steps from starting position of the piece."""
        self.steps_from_start = steps

    def set_my_player(self, my_player):
        """Sets the owner of the piece"""
        self.my_player = my_player

    def check_safe_point(self):
        """Checks if the piece position is a safe spot."""
        pos = self.get_position()
        if pos in [8, 21, 34, 47]:
            return True
        elif pos is not None and self.get_steps_from_start() == 0:
            return True
        return False

    def check_home_run(self):
        """
        Check if piece is in home run and can be move/is playable.
        :return: False = Piece can't be moved, True = Piece can moved
        """
        piece_pos = self.get_steps_from_start()
        if piece_pos == 50 and self.my_player.roll == 6:
            return True
        if piece_pos in range(51, 56) and \
           (self.my_player.roll + piece_pos) > 55:
            return True
        return False

    def check_space_empty(self, future_pos):
        """
        Checks if the square/space, the piece is moving onto is
        on home run and empty.
        :param future_pos: future position of piece
        :return: False = Not empty, True = Empty
        """
        for piece in self.my_player.my_pieces:
            piece_pos = piece.get_steps_from_start()
            # Check if space, piece is moving onto, has piece already on it.
            if piece_pos in range(51, 56) and future_pos == piece_pos:
                return False
        return True  # Space is empty

    def check_forward_movement(self):
        """
        Check if forward position is playable/possible for this piece.
        :return: False = Piece not able to move, True = Piece able to move
        """
        future_pos = self.get_steps_from_start() + self.my_player.roll
        # future position of piece
        if (future_pos in range(51, 56) or future_pos > 55) and \
           self.check_space_empty(future_pos) is False:
            return False
        return True
