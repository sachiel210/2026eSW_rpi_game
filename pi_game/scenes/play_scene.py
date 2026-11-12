from scenes.scene import Scene
from game_map import GameMap
from player import Player
from settings import W, H, DIRECTION

class PlayScene(Scene):
    def __init__(self, stage):
        self.stage = stage
        self.reset()

    def reset(self):
        # 게임 맵 초기화
        self.game_map = GameMap(self.stage.layout)

        # 장애물 상태 초기화
        self.obstacles = self.game_map.obstacles

        # 플레이어 초기화
        self.player = Player(self.game_map.player_start)

        # 턴 수 초기화
        self.moves = self.stage.moves
s
        # 게임 클리어 여부 초기화
        self.clear = False
        self.game_over = False

    def end_turn(self, cost, position):
        for ob in self.obstacles:
            ob.next_turn()
            if ob.passable and ob.position == position:
                cost += ob.step_cost()

        self.moves -= cost
        if self.player.position == self.game_map.goal:
            self.clear = True
        elif self.moves <= 0:
            self.game_over = True

    # 막힌 공간인지 확인 (바위를 밀어 넣지 못하는 공간)
    def is_blocked(self, position):
        if self.game_map.is_wall(position):
            return True

        for ob in self.obstacles:
            if not ob.passable and ob.position == position:
                return True
        if position == self.game_map.goal:
            return True
        return False

    # 가는 길에 장애물이 있는지 확인
    def blocking_at(self, position):
        for ob in self.obstacles:
            if not ob.passable and ob.position == position:
                return ob
        return None

    def handle(self, name):
        if name in DIRECTION and not self.clear and not self.game_over:
            target = self.player.next_position(DIRECTION[name])
            cost = 0

            if not self.game_map.is_wall(target):
                ob = self.blocking_at(target)
                if ob:
                    cost = ob.kick(DIRECTION[name], self.is_blocked, self.player)
                else:
                    self.player.position = target
                    cost = 1
                    if target == self.game_map.key:
                        self.player.has_key = True
                        self.game_map.key = None

            alive_obstacles = []
            for ob in self.obstacles:
                if ob.alive:
                    alive_obstacles.append(ob)
            self.obstacles = alive_obstacles

            if cost > 0:
                self.end_turn(cost, self.player.position)

        elif name == "B":
            self.reset()

        return self

    def draw(self, img, pen):
        pen.rectangle((0, 0, W - 1, H - 1), fill = (15, 10, 20))
        self.game_map.draw(pen)

        pen.text((8, 10), "MOVES " + str(self.moves), fill = (255, 255, 255))

        if self.player.has_key:
            self.game_map.draw_key(pen, (80, 4, 101, 25), (15, 10, 20))

        for ob in self.obstacles:
            if ob.passable:
                ob.draw(pen, self.game_map.cell_box)
        for ob in self.obstacles:
            if not ob.passable:
                ob.draw(pen, self.game_map.cell_box)

        self.player.draw(pen, self.game_map.cell_box)

        # 스테이지 통과, 실패 시 출력
        if self.clear:
            pen.text((150, 10), "CLEAR!", fill = (255, 255, 255))
        elif self.game_over:
            pen.text((150, 10), "FAIL", fill = (255, 255, 255))
