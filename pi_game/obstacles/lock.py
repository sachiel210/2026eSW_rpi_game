from obstacles.obstacle import Obstacle

class Lock(Obstacle):
    def kick(self, direction, is_blocked, player):
        if player.has_key:
            player.has_key = False
            self.alive = False
            return 0
        else:
            return 1

    def draw(self, pen, cell_box):
        left, top, right, bottom = cell_box(self.position, 3)
        center = (left + right) // 2
        hole = (255, 210, 0)

        # 상자 (금색 테두리)
        pen.rectangle((left, top, right, bottom), fill=(20, 15, 10), outline=(255, 210, 0), width=2)

        # 열쇠 구멍: 위쪽 동그라미 + 아래로 퍼지는 삼각형
        pen.ellipse((center - 3, top + 6, center + 3, top + 12), fill=hole)
        pen.polygon([(center - 3, bottom - 5), (center, top + 9), (center + 3, bottom - 5)], fill=hole)