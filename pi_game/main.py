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

def end_turn(cost, position):
    global moves, clear, game_over

    for ob in obstacles:
        ob.next_turn()
        if ob.passable and ob.position == position:
            cost += ob.step_cost()

    moves -= cost
    if player.position == game_map.goal:
        clear = True
    elif moves <= 0:
        game_over = True

# 막힌 공간인지 확인 (바위를 밀어 넣지 못하는 공간)
def is_blocked(position):
    if game_map.is_wall(position):
        return True

    for ob in obstacles:
        if not ob.passable and ob.position == position:
            return True
    if position == game_map.goal:
        return True
    return False

# 가는 길에 장애물이 있는지 확인
def blocking_at(position):
    for ob in obstacles:
        if not ob.passable and ob.position == position:
            return ob
    return None
    
# 방향 딕셔너리
DIRECTION = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0)
}

# 게임 스테이지
stage = STAGES[0]


def render():
    draw.rectangle((0, 0, W - 1, H - 1), fill = (15, 10, 20))
    game_map.draw(draw)

    draw.text((8, 10), "MOVES " + str(moves), fill = (255, 255, 255))

    if player.has_key:
        game_map.draw_key(draw, (80, 4, 101, 25), (15, 10, 20))

    for ob in obstacles:
        if ob.passable:
            ob.draw(draw, game_map.cell_box)
    for ob in obstacles:
        if not ob.passable:
            ob.draw(draw, game_map.cell_box)

    player.draw(draw, game_map.cell_box)

    # 스테이지 통과, 실패 시 출력
    if clear:
        draw.text((100, 10), "CLEAR!", fill = (255, 255, 255))
    elif game_over:
        draw.text((100, 10), "FAIL", fill = (255, 255, 255))

    # lcd로 출력 
    disp.image(img)

def reset():
    global game_map, obstacles, player, moves, clear, game_over

    # 게임 맵 초기화
    game_map = GameMap(stage.layout)

    # 장애물 상태 초기화
    obstacles = game_map.obstacles

    # 플레이어 초기화
    player = Player(game_map.player_start)

    # 턴 수 초기화
    moves = stage.moves

    # 게임 클리어 여부 초기화
    clear = False
    game_over = False

reset()

try:
    render()
    while True:
        for name in read_just_pressed():
            if name in DIRECTION and not clear and not game_over:
                target = player.next_position(DIRECTION[name])
                cost = 0

                if not game_map.is_wall(target):
                    ob = blocking_at(target)
                    if ob:
                        cost = ob.kick(DIRECTION[name], is_blocked, player)
                    else:
                        player.position = target
                        cost = 1
                        if target == game_map.key:
                            player.has_key = True
                            game_map.key = None

                alive_obstacles = []
                for ob in obstacles:
                    if ob.alive:
                        alive_obstacles.append(ob)
                obstacles = alive_obstacles

                if cost > 0:
                    end_turn(cost, player.position)
                render()

            # B 버튼(위 버튼) 누르면 초기화
            elif name == "B":
                reset()
                render()

        time.sleep(1 / FPS)

except KeyboardInterrupt:
    pass

finally:
    disp.image(Image.new("RGB", (W, H)))
    backlight.value = False