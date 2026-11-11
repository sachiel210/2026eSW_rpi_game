import time
import board, digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7789

from game_map import GameMap
from player import Player
from stages import STAGES

W = H = 240
FPS = 20

# 제어 핀
cs = digitalio.DigitalInOut(board.CE0)
dc = digitalio.DigitalInOut(board.D25)
rst = digitalio.DigitalInOut(board.D24)

# 백라이트
backlight = digitalio.DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True

# LCD 객체
disp = st7789.ST7789(board.SPI(), width = W, height = H, rotation = 180, y_offset=80,
                     cs = cs, dc = dc, rst = rst, baudrate = 24000000)

def btn(pin):
    d = digitalio.DigitalInOut(pin)
    d.direction = digitalio.Direction.INPUT
    d.pull = digitalio.Pull.UP
    return d

UP, DOWN = btn(board.D17), btn(board.D22)
LEFT, RIGHT = btn(board.D27), btn(board.D23)
CENTER = btn(board.D4)
A, B = btn(board.D5), btn(board.D6)

# 화면 설정
img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)

BUTTONS = {"UP": UP, "DOWN": DOWN, "LEFT": LEFT, "RIGHT": RIGHT,
           "CENTER": CENTER, "A": A, "B": B}

prev = {}
for name in BUTTONS:
    prev[name] = False # False를 안 누른 상태로 생각

def read_just_pressed():
    # 이번에 처음 눌린 버튼 목록
    global prev
    now = {}

    for name, b in BUTTONS.items():
        now[name] = not b.value # 핀 값 불러오기
        
    pressed = [] # 눌린 버튼
    for i in BUTTONS:
        if now[i] and not prev[i]:
            pressed.append(i)

    prev = now
    return pressed

def end_turn(cost):
    global moves, clear, game_over
    moves -= cost
    if player.position == game_map.goal:
        clear = True
    elif moves <= 0:
        game_over = True

# 방향 딕셔너리
DIRECTION = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0)
}

# 게임 스테이지
stage = STAGES[0]

# 게임 맵
game_map = GameMap(stage.layout)

# 게임 플레이어
player = Player(game_map.player_start)

# 턴 수
moves = stage.moves

# 클리어, 게임오버
clear = False
game_over = False

def render():
    draw.rectangle((0, 0, W - 1, H - 1), fill = (15, 10, 20))
    game_map.draw(draw)
    player.draw(draw, game_map.cell_box)

    draw.text((8, 10), "MOVES " + str(moves), fill = (255, 255, 255))

    # 스테이지 통과, 실패 시 출력
    if clear:
        draw.text((100, 10), "CLEAR!", fill = (255, 255, 255))
    elif game_over:
        draw.text((100, 10), "FAIL", fill = (255, 255, 255))

    # lcd로 출력 
    disp.image(img)

try:
    render()
    while True:
        for name in read_just_pressed():
            if name in DIRECTION and not clear and not game_over:
                target = player.next_position(DIRECTION[name])
                cost = 0

                if not game_map.is_wall(target):
                    player.position = target
                    cost = 1

                if cost > 0:
                    end_turn(cost)
                    render()

            # B 버튼(위 버튼) 누르면 초기화
            elif name == "B":
                # 플레이어 위치 초기화
                player.position = game_map.player_start

                # 남은 턴 초기화
                moves = stage.moves
                
                # 게임 상태 초기화
                clear = False
                game_over = False
                render()

        time.sleep(1 / FPS)

except KeyboardInterrupt:
    pass

finally:
    disp.image(Image.new("RGB", (W, H)))
    backlight.value = False