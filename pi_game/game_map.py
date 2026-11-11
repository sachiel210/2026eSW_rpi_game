TILE = 30
INFO = 30
SCREEN = 240

class GameMap:
    def __init__(self, stage):
        self.rows = len(stage) # 열 길이 (7)
        self.cols = len(stage[0]) # 행 길이 (8)

        # 맵 좌상단 좌표
        self.origin_x = (SCREEN - self.cols * TILE) // 2
        self.origin_y = INFO + (SCREEN - INFO - self.rows * TILE) // 2

        # 벽 집합
        self.walls = set()
        for y in range(self.rows):
            for x in range(self.cols):
                if stage[y][x] == "#":
                    self.walls.add((x, y))
                elif stage[y][x] == "P":
                    self.player_start = (x, y)

    def cell_box(self, position, pad = 0):
        # 각 타일의 좌표를 픽셀 위치로 바꿔주는 함수
        # pad는 여백을 의미한다
        x, y = position
        left = self.origin_x + x * TILE
        top = self.origin_y + y * TILE
        return (left + pad, top + pad, left + TILE - 1 - pad, top + TILE - 1 - pad)

    def in_bounds(self, position):
        x, y = position
        return 0 <= x < self.cols and 0 <= y < self.rows

    def is_wall(self, position):
        return not self.in_bounds(position) or position in self.walls

    def draw(self, draw):
        for y in range(self.rows):
            for x in range(self.cols):
                if (x, y) in self.walls:
                    draw.rectangle(self.cell_box((x, y)), fill = (70, 55, 60))
                else:
                    draw.rectangle(self.cell_box((x, y)), fill=(35, 30, 40), outline=(45, 40, 50))

        # 테두리 그리기
        right = self.origin_x + self.cols * TILE - 1
        bottom = self.origin_y + self.rows * TILE - 1
        draw.rectangle((self.origin_x, self.origin_y, right, bottom), outline=(150, 120, 140), width=2)