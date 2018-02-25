from box_and_button import Box
from constants import BLACK
class ScoreBoard():
    def __init__(self,all_pieces):
        self._rows = 1
        self._cols = 2
        self.list_of_pieces = all_pieces

    def draw(self,
	     w=100,h=30,y=500,x=900,
	     row_titles=["Color","Score"]):
        initial_x = x
        for i in row_titles:
            Box(i, x, y, w, h, BLACK, 1).draw()
            x += w   
        pieces_dict = {piece.colour:0 for piece in self.list_of_pieces}
        for piece in self.list_of_pieces:
            pieces_dict[piece.colour] += piece.get_steps_from_start()
        
        for piece in pieces_dict:
            # And draw the 4 players on the scoreboard.
            y += h
            x = initial_x
            color_field = Box(piece, x, y, w, h, BLACK, 1)
            color_field.draw()
            x += w
            score_field = Box(str(pieces_dict[piece]), x, y, w, h, BLACK, 1)
            score_field.draw()
            x += w
