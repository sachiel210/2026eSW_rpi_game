from obstacles.rock import Rock
from obstacles.monster import Monster
from obstacles.spike import Spike
from obstacles.spike import ToggleSpike
from obstacles.lock import Lock

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

        # 장애물 리스트
        self.obstacles = []

        for y in range(self.rows):
            for x in range(self.cols):
                if stage[y][x] == "#":
                    self.walls.add((x, y))
                elif stage[y][x] == "P":
                    self.player_start = (x, y)
                elif stage[y][x] == "G":
                    self.goal = (x, y)
                elif stage[y][x] == "R":
                    self.obstacles.append(Rock((x, y)))
                elif stage[y][x] == "M":
                    self.obstacles.append(Monster((x, y)))
                elif stage[y][x] == "S":
                    self.obstacles.append(Spike((x, y)))
                elif stage[y][x] == "T":
                    self.obstacles.append(ToggleSpike((x, y), True))
                elif stage[y][x] == "t":
                    self.obstacles.append(ToggleSpike((x, y), False))
                elif stage[y][x] == "L":
                    self.obstacles.append(Lock((x, y)))
                elif stage[y][x] == "K":
                    self.key = (x, y)

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

    # 특정 좌표가 벽인지 확인
    def is_wall(self, position):
        return not self.in_bounds(position) or position in self.walls

    def draw_key(self, pen, box, hole_color):
        left, top, right, bottom = box
        middle = (top + bottom) // 2
        gold = (255, 210, 0)

        pen.ellipse((left, middle - 5, left + 10, middle + 5), fill=gold)
        pen.ellipse((left + 3, middle - 2, left + 7, middle + 2), fill=hole_color)
        pen.rectangle((left + 9, middle - 1, right, middle + 1), fill=gold)
        pen.rectangle((right - 6, middle + 1, right - 5, middle + 5), fill=gold)
        pen.rectangle((right - 2, middle + 1, right, middle + 4), fill=gold)

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

        draw.rectangle(self.cell_box(self.goal, 3), outline=(0, 230, 120), width=3)

        # 열쇠 그리기
        if self.key:
            self.draw_key(draw, self.cell_box(self.key, 4), (35, 30, 40))