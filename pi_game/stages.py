# 데이터 클래스 형태로 각 스테이지 저장

class Stage:
    def __init__(self, layout, moves, npc = None):
        # 맵(행렬 형태로 저장)
        # P: Player 시작 위치
        # #: 통과 불가능한 벽
        # .: 빈 공간
        self.layout = layout

        # 한 스테이지에 움직일 수 있는 턴
        self.moves = moves

        # 각 스테이지 끝에서 나오는 npc
        self.npc = npc

STAGES = [
    Stage(
        layout = [
            "P.MRRS..",
            ".###.T.S",
            ".#...t..",
            "R#...###",
            "t....#.#",
            ".....#.#",
            "...K.L.G",
        ],
        moves = 20,
    )
]