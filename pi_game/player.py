class Player:
    def __init__(self, position):
        self.position = position

    def next_position(self, direction):
        x, y = self.position
        return (x + direction[0], y + direction[1])

    def draw(self, draw, cell_box):
        draw.ellipse(cell_box(self.position, 4), fill = (0, 200, 230))
