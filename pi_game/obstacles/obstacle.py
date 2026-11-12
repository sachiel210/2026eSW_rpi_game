# 장애물 super class
class Obstacle:
    passable = False
    
    def __init__(self, position):
        self.position = position
        self.alive = True

    def kick(self, direction, is_blocked, player):
        return 1

    def step_cost(self):
        return 0

    def next_turn(self):
        pass

    def draw(self, pen, cell_box):
        pass
