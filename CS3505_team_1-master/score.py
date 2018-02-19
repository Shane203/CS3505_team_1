from box_and_button import Box
from constants import BLACK
class ScoreBoard():
    def __init__(self):
        self._rows = 1
        self._cols = 2

    def draw(self, list_of_pieces):
        w = 100
        h = 30
        y = 500
        x = 900
        red_score = 0
        blue_score = 0
        green_score = 0
        yellow_score = 0
        color = Box("Color", x, y, w, h, BLACK, 1)
        x += w
        score = Box("Score", x, y, w, h, BLACK, 1)
        x += w
        color.draw()
        score.draw()
        for piece in list_of_pieces:
            if piece.colour == "red":
                red_score += piece.get_steps_from_start()
            elif piece.colour == "blue":
                blue_score += piece.get_steps_from_start()
            elif piece.colour == "green":
                green_score += piece.get_steps_from_start()
            elif piece.colour == "yellow":
                yellow_score += piece.get_steps_from_start()

        list_of_scores = [(red_score, "red"), (blue_score, "blue"),
                          (green_score, "green"), (yellow_score, "yellow")]
        list_of_scores = sorted(list_of_scores)[::-1]
        for i in list_of_scores:
            # Access each player, sort them by score.
            # And draw the 4 players on the scoreboard.
            y += h
            x = 900
            color_field = Box(i[1], x, y, w, h, BLACK, 1)
            color_field.draw()
            x += w
            score_field = Box(str(i[0]), x, y, w, h, BLACK, 1)
            score_field.draw()
            x += w
