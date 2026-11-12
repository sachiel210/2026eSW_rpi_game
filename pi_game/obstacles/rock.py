from obstacles.obstacle import Obstacle

class Rock(Obstacle):
    def kick(self, direction, is_blocked, player):
        x, y = self.position
        dx, dy = direction
        target = (x + dx, y + dy)

        if is_blocked(target):
            self.on_blocked()
        else:
            self.position = target
        return 1

    def on_blocked(self):
        pass

    def draw(self, pen, cell_box):
        pen.ellipse(cell_box(self.position, 3), fill = (140, 140, 150))