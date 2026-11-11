import time
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

# ---------------- 설정 ----------------
TILE = 30
HUD_H = 30
MOVE_LIMIT = 17

#  # 벽   . 바닥   P 플레이어
#  B 바위(밀 수 있음)   K 열쇠(밟으면 획득)   C 상자(열쇠가 있으면 열림 → 클리어)
LEVEL = [
    "########",
    "#P.#..K#",
    "#.B#.B.#",
    "#..B...#",
    "#.##B#.#",
    "#...#.C#",
    "########",
]

# ---------------- 하드웨어 ----------------
cs = digitalio.DigitalInOut(board.CE0)
dc = digitalio.DigitalInOut(board.D25)
rst = digitalio.DigitalInOut(board.D24)
backlight = digitalio.DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True
disp = st7789.ST7789(board.SPI(), width=240, height=240, rotation=180, y_offset=80,
                     cs=cs, dc=dc, rst=rst, baudrate=24000000)

def make_button(pin):
    b = digitalio.DigitalInOut(pin)
    b.direction = digitalio.Direction.INPUT
    b.pull = digitalio.Pull.UP
    return b

BUTTONS = {
    "UP": make_button(board.D17), "DOWN": make_button(board.D22),
    "LEFT": make_button(board.D27), "RIGHT": make_button(board.D23),
    "A": make_button(board.D5), "B": make_button(board.D6),
}
prev = {name: False for name in BUTTONS}

def read_just_pressed():
    """이번에 '처음' 눌린 버튼 이름 목록 (누르고 있어도 한 번만 인식)"""
    global prev
    now = {name: not b.value for name, b in BUTTONS.items()}
    pressed = [n for n in BUTTONS if now[n] and not prev[n]]
    prev = now
    return pressed

# ---------------- 게임 로직 ----------------
DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.walls, self.boulders = set(), set()
        self.key = None
        for y, row in enumerate(LEVEL):
            for x, c in enumerate(row):
                if c == "#": self.walls.add((x, y))
                elif c == "B": self.boulders.add((x, y))
                elif c == "K": self.key = (x, y)
                elif c == "C": self.chest = (x, y)
                elif c == "P": self.player = (x, y)
        self.has_key = False
        self.moves = MOVE_LIMIT
        self.state = "play"          # play / clear / fail

    def is_blocked(self, pos):
        """바위가 밀려 들어갈 수 없는 칸"""
        return (pos in self.walls or pos in self.boulders
                or pos == self.chest or pos == self.key)

    def move(self, d):
        dx, dy = d
        target = (self.player[0] + dx, self.player[1] + dy)
        beyond = (target[0] + dx, target[1] + dy)

        if target in self.walls:
            return                          # 벽: 아무 일 없음 (이동 소모 X)

        if target == self.chest:
            if not self.has_key:
                return                      # 열쇠 없이 상자: 아무 일 없음 (이동 소모 X)
            self.moves -= 1
            self.state = "clear"            # 열쇠로 상자 열기 → 클리어
            return

        if target in self.boulders:         # 바위 밀기 (막혀 있으면 안 밀리지만 이동은 소모)
            if not self.is_blocked(beyond):
                self.boulders.remove(target)
                self.boulders.add(beyond)
        else:
            self.player = target            # 빈 칸 또는 열쇠 칸으로 이동
            if target == self.key:
                self.has_key = True
                self.key = None             # 열쇠는 맵에서 사라짐

        self.moves -= 1
        if self.moves <= 0:
            self.state = "fail"

# ---------------- 그리기 ----------------
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
BIG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
screen = Image.new("RGB", (240, 240))
draw = ImageDraw.Draw(screen)

def cell_box(pos, pad=0):
    x, y = pos
    left, top = x * TILE, HUD_H + y * TILE
    return (left + pad, top + pad, left + TILE - 1 - pad, top + TILE - 1 - pad)

def center_text(text, y, font, color):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw.text(((240 - (r - l)) // 2, y), text, font=font, fill=color)

def draw_key(left, top):
    """(left, top)을 기준으로 작은 열쇠 그림"""
    gold = (255, 210, 0)
    draw.ellipse((left, top + 4, left + 10, top + 14), outline=gold, width=3)    # 손잡이 고리
    draw.rectangle((left + 10, top + 8, left + 22, top + 10), fill=gold)         # 몸통
    draw.rectangle((left + 17, top + 10, left + 19, top + 14), fill=gold)        # 톱니
    draw.rectangle((left + 21, top + 10, left + 22, top + 13), fill=gold)

def draw_chest(pos, opened=False):
    l, t, r, b = cell_box(pos, 3)
    draw.rectangle((l, t + 4, r, b), fill=(140, 85, 35), outline=(90, 50, 20))   # 상자 몸통
    draw.line((l, t + 11, r, t + 11), fill=(90, 50, 20), width=2)                # 뚜껑 경계
    lock = (220, 190, 60) if opened else (200, 200, 200)
    mx = (l + r) // 2
    draw.rectangle((mx - 3, t + 9, mx + 3, t + 16), fill=lock)                   # 자물쇠

def render(game):
    draw.rectangle((0, 0, 239, 239), fill=(15, 10, 20))

    # 상단 정보 표시줄
    color = (255, 255, 255) if game.moves > 3 else (255, 80, 80)
    draw.text((8, 6), f"MOVES {game.moves}", font=FONT, fill=color)
    if game.has_key:
        draw_key(110, 5)
    draw.text((150, 6), "B:RESET", font=FONT, fill=(150, 150, 150))

    # 맵
    for y, row in enumerate(LEVEL):
        for x, _ in enumerate(row):
            pos = (x, y)
            if pos in game.walls:
                draw.rectangle(cell_box(pos), fill=(70, 55, 60))
            else:
                draw.rectangle(cell_box(pos), fill=(35, 30, 40), outline=(45, 40, 50))

    if game.key:
        l, t, _, _ = cell_box(game.key)
        draw_key(l + 4, t + 6)
    draw_chest(game.chest, opened=(game.state == "clear"))

    for pos in game.boulders:
        draw.ellipse(cell_box(pos, 3), fill=(140, 140, 150), outline=(200, 200, 210))

    draw.ellipse(cell_box(game.player, 4), fill=(0, 200, 230), outline=(255, 255, 255))

    # 결과 화면
    if game.state != "play":
        draw.rectangle((20, 80, 219, 170), fill=(0, 0, 0), outline=(255, 255, 255))
        if game.state == "clear":
            center_text("CLEAR!", 95, BIG, (255, 210, 0))
        else:
            center_text("NO MOVES", 95, BIG, (255, 80, 80))
        center_text("A: RETRY", 135, FONT, (255, 255, 255))

    disp.image(screen)

# ---------------- 메인 루프 ----------------
def main():
    game = Game()
    render(game)
    while True:
        changed = False
        for name in read_just_pressed():
            if name == "B" or (name == "A" and game.state != "play"):
                game.reset()
                changed = True
            elif name in DIRS and game.state == "play":
                game.move(DIRS[name])
                changed = True
        if changed:
            render(game)
        time.sleep(1 / 60)

try:
    main()
except KeyboardInterrupt:
    pass
finally:
    disp.image(Image.new("RGB", (240, 240)))
    backlight.value = False