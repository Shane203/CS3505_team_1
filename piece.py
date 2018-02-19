import pygame

class Piece(object):
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
        string = "(%s-%d-%s)" % (self.colour, self.number, self.position)
        return string

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    def get_steps_from_start(self):
        return self.steps_from_start

    def set_steps_from_start(self, steps):
        self.steps_from_start = steps

    def set_my_player(self, my_player):
        self.my_player = my_player

    def check_safe_point(self):
        if self.get_position() in [8, 21, 34, 47]:
            return True
        elif self.get_position() is not None and self.get_steps_from_start() == 0:
            return True
        return False

    def check_home_run(self):
        """
        Check if piece is in home run and can be move/is playable.
        :param piece: current piece to be checked
        :return: False = Piece can't be moved, True = Piece can moved
        """
        piece_pos = self.get_steps_from_start()
        if piece_pos == 50 and self.my_player.roll == 6:
            return True
        if piece_pos in range(51, 56) and (self.my_player.roll + piece_pos) > 55:
            return True
        return False

    def check_space_empty(self, future_pos):
        """
        Checks if the square/space, the piece is moving onto is on home run and empty.
        :param future_pos: future position of piece
        :return: False = Not empty, True = Empty
        """
        for piece in self.my_player.my_pieces:
            piece_pos = piece.get_steps_from_start()
            if piece_pos in range(51, 56) and future_pos == piece_pos:  # Check if space, piece is moving onto, has piece already on it.
                return False
        return True  # Space is empty

    def check_forward_movement(self):
        """
        Check if forward position is playable/possible for this piece.
        :param piece: current piece
        :var future_pos: future position of piece = current position and dice roll
        :return: False = Piece not playable, True =
        """
        future_pos = self.get_steps_from_start() + self.my_player.roll
        if (future_pos in range(51, 56) or future_pos > 55) and self.check_space_empty(future_pos) is False:
            return False
        return True
