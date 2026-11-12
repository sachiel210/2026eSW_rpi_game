from obstacles.rock import Rock

class Monster(Rock):
    def on_blocked(self):
        self.alive = False
        
    def draw(self, pen, cell_box):
        left, top, right, bottom = cell_box(self.position, 5)

        # 빨간 몸
        pen.rectangle((left, top, right, bottom), fill=(210, 50, 50))

        # 흰 눈
        pen.rectangle((left + 4, top + 6, left + 7, top + 10), fill=(255, 255, 255))
        pen.rectangle((right - 7, top + 6, right - 4, top + 10), fill=(255, 255, 255))