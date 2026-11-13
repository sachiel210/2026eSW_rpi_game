import time
import board, digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7789

from stages import STAGES
from settings import W, H, FPS
from scenes.play_scene import PlayScene
from scenes.title_scene import TitleScene

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

# 버튼 변수
UP, DOWN = btn(board.D17), btn(board.D22)
LEFT, RIGHT = btn(board.D27), btn(board.D23)
CENTER = btn(board.D4)
A, B = btn(board.D5), btn(board.D6)

# 화면 설정
img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)

# 버튼 딕셔너리
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

    # 이번 프레임에 처음 누른 버튼 저장
    prev = now
    return pressed

# 화면 그리기 함수
def render():
    scene.draw(img, draw)
    disp.image(img)

# 게임 장면
# 메뉴, 인게임, 대화창 3종류
scene = TitleScene()

try:
    render()

    # gmae loop
    while True:
        pressed = read_just_pressed()

        # 눌린 버튼을 scene에 넘김
        for name in pressed:
            scene = scene.handle(name)

        if pressed or scene.update():
            render()

        # 틱
        time.sleep(1 / FPS)

except KeyboardInterrupt:
    pass

finally:
    # 화면 끄고 종료
    disp.image(Image.new("RGB", (W, H)))
    backlight.value = False