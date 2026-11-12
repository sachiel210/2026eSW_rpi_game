from obstacles.obstacle import Obstacle

class Spike(Obstacle):
    passable = True

    def step_cost(self):
        return 1

    def draw_holes(self, pen, cell_box):
        left, top, right, bottom = cell_box(self.position, 6)
        width = right - left

        for i in range(3):
            x = left + width * i // 2
            pen.ellipse((x - 2, bottom - 3, x + 2, bottom + 1), fill=(20, 20, 25))

    def draw_spikes(self, pen, cell_box):
        left, top, right, bottom = cell_box(self.position, 6)
        width = right - left
        
        for i in range(3):
            x = left + width * i // 2
            pen.polygon([(x - 3, bottom), (x, top + 4), (x + 3, bottom)], fill=(200, 200, 210))

    def draw(self, pen, cell_box):
        self.draw_holes(pen, cell_box)
        self.draw_spikes(pen, cell_box)

class ToggleSpike(Spike):
    def __init__(self, position, up):
        super().__init__(position)
        self.up = up

    def next_turn(self):
        if self.up:
            self.up = False
        else:
            self.up = True

    def step_cost(self):
        if self.up:
            return 1
        return 0

    def draw(self, pen, cell_box):
        self.draw_holes(pen, cell_box)
        if self.up:
            self.draw_spikes(pen, cell_box)