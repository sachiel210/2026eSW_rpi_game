import os
import sys
import time
import random
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

# =========================================================
# 1. 하드웨어 설정
# =========================================================
W = H = 240
FPS = 30

cs = digitalio.DigitalInOut(board.CE0)
dc = digitalio.DigitalInOut(board.D25)
rst = digitalio.DigitalInOut(board.D24)

backlight = digitalio.DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True

disp = st7789.ST7789(board.SPI(), width=W, height=H, rotation=180, y_offset=80,
                     cs=cs, dc=dc, rst=rst, baudrate=24000000)

def btn(pin):
    d = digitalio.DigitalInOut(pin)
    d.direction = digitalio.Direction.INPUT
    d.pull = digitalio.Pull.UP
    return d

BUTTONS = {
    "UP": btn(board.D17), "DOWN": btn(board.D22),
    "A": btn(board.D5), "B": btn(board.D6),
}
prev = {name: False for name in BUTTONS}

def read_just_pressed():
    global prev
    now = {name: not b.value for name, b in BUTTONS.items()}
    pressed = [n for n in BUTTONS if now[n] and not prev[n]]
    prev = now
    return pressed

img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)

# =========================================================
# 2. 폰트, 캐릭터 이미지
# =========================================================
HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(HERE, "assets")

FONT_PATH = None
for path in ["/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
             os.path.join(ASSET_DIR, "NanumGothic.ttf")]:
    if os.path.exists(path):
        FONT_PATH = path
        break
if FONT_PATH is None:
    print("한글 폰트가 없습니다. fonts-nanum을 설치하거나 assets/NanumGothic.ttf를 넣어 주세요.")
    sys.exit(1)

FONT = ImageFont.truetype(FONT_PATH, 14)
SMALL = ImageFont.truetype(FONT_PATH, 11)
BIG = ImageFont.truetype(FONT_PATH, 24)

def load_portrait(key):
    pic = Image.open(os.path.join(ASSET_DIR, key + ".png")).convert("RGBA")
    return pic.resize((150, 150), Image.LANCZOS)

PORTRAIT = {k: load_portrait(k) for k in ["seori", "yeoreum", "eunbit"]}

# 말하는 사람: (화면에 보일 이름, 이름 색)
SPEAKERS = {
    "me":      ("나",   (160, 220, 255)),
    "seori":   ("서리", (170, 200, 245)),
    "yeoreum": ("여름", (255, 215, 110)),
    "eunbit":  ("은빛", (210, 190, 255)),
}

# =========================================================
# 3. 배경 (코드로 그려서 시작할 때 한 번만 만들어 둠)
# =========================================================
def gradient(top, bottom):
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / (H - 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line((0, y, W - 1, y), fill=color)
    return bg, d

def bg_campus():
    bg, d = gradient((140, 185, 230), (215, 232, 245))
    d.rectangle((0, 120, 110, 239), fill=(150, 160, 185))          # 건물 1
    d.rectangle((130, 95, 239, 239), fill=(135, 145, 175))         # 건물 2
    for x in range(12, 100, 22):
        for y in range(132, 200, 22):
            d.rectangle((x, y, x + 10, y + 12), fill=(200, 215, 235))
    for x in range(142, 230, 22):
        for y in range(108, 200, 22):
            d.rectangle((x, y, x + 10, y + 12), fill=(190, 205, 230))
    d.rectangle((0, 205, 239, 239), fill=(120, 150, 110))          # 잔디
    return bg

def bg_classroom():
    bg, d = gradient((240, 228, 205), (215, 195, 165))
    d.rectangle((30, 25, 210, 95), fill=(45, 85, 65), outline=(120, 90, 60), width=4)  # 칠판
    d.line((50, 50, 120, 50), fill=(220, 230, 220), width=2)
    d.line((50, 65, 150, 65), fill=(220, 230, 220), width=2)
    for y in (170, 205):                                           # 책상 줄
        d.rectangle((0, y, 239, y + 8), fill=(160, 120, 80))
    return bg

def bg_cafeteria():
    bg, d = gradient((252, 222, 180), (232, 185, 140))
    d.rectangle((0, 30, 239, 60), fill=(200, 150, 110))            # 배식대
    for x in (20, 130):
        d.rectangle((x, 170, x + 90, 182), fill=(240, 240, 235))   # 테이블
        d.rectangle((x + 10, 182, x + 16, 230), fill=(180, 180, 175))
        d.rectangle((x + 74, 182, x + 80, 230), fill=(180, 180, 175))
    return bg

def bg_library():
    bg, d = gradient((95, 65, 48), (60, 40, 30))
    rnd = random.Random(7)                                         # 항상 같은 모양
    for row in range(5):
        y = 15 + row * 45
        d.rectangle((0, y + 34, 239, y + 40), fill=(120, 85, 55))  # 선반
        x = 4
        while x < 236:
            w = rnd.randint(6, 12)
            h = rnd.randint(22, 33)
            color = rnd.choice([(170, 60, 60), (60, 100, 150), (200, 170, 90),
                                (80, 130, 90), (140, 100, 160), (210, 200, 180)])
            d.rectangle((x, y + 34 - h, x + w - 1, y + 33), fill=color)
            x += w + 1
    return bg

def bg_clubroom():
    bg, d = gradient((205, 195, 225), (165, 155, 195))
    d.rectangle((20, 30, 80, 100), fill=(250, 250, 245), outline=(90, 80, 110), width=2)   # 사진 액자
    d.rectangle((30, 40, 70, 80), fill=(140, 180, 220))
    d.rectangle((100, 25, 150, 75), fill=(250, 250, 245), outline=(90, 80, 110), width=2)
    d.rectangle((108, 33, 142, 60), fill=(230, 170, 150))
    d.rectangle((0, 190, 239, 239), fill=(120, 100, 90))           # 책상
    return bg

def bg_festival():
    bg, d = gradient((15, 15, 55), (60, 30, 85))
    rnd = random.Random(3)
    for _ in range(40):                                            # 별
        x, y = rnd.randint(0, 239), rnd.randint(0, 120)
        d.point((x, y), fill=(255, 255, 230))
    for i in range(24):                                            # 전구 줄
        x = i * 10 + 5
        y = 60 + int(((x - 120) / 120) ** 2 * 25)
        color = [(255, 200, 80), (255, 120, 150), (120, 220, 255)][i % 3]
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=color)
    d.rectangle((0, 200, 239, 239), fill=(40, 30, 50))             # 운동장
    return bg

def bg_snow():
    bg, d = gradient((25, 35, 75), (85, 95, 135))
    d.rectangle((0, 205, 239, 239), fill=(225, 230, 240))          # 쌓인 눈
    return bg

BACKGROUNDS = {
    "campus":    ("캠퍼스",       bg_campus()),
    "classroom": ("강의실",       bg_classroom()),
    "cafeteria": ("학생식당",     bg_cafeteria()),
    "library":   ("도서관 3층",   bg_library()),
    "clubroom":  ("사진 동아리방", bg_clubroom()),
    "festival":  ("축제 마지막 밤", bg_festival()),
    "snow":      ("",            bg_snow()),
}

# 눈송이 [x, y, 떨어지는 속도]
snowflakes = [[random.randint(0, 239), random.randint(0, 239), random.uniform(0.6, 1.8)]
              for _ in range(45)]

def update_snow():
    for f in snowflakes:
        f[1] += f[2]
        f[0] += random.uniform(-0.4, 0.4)
        if f[1] > H:
            f[0], f[1] = random.randint(0, 239), -3

def draw_snow():
    for x, y, s in snowflakes:
        r = 1 if s < 1.2 else 2
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255))

# =========================================================
# 4. 시나리오
#   ("label", 이름)            : 점프 목적지
#   ("bg", 배경)               : 배경 바꾸기
#   ("show", 캐릭터) / ("hide",) : 캐릭터 그림 보이기 / 숨기기
#   ("say", 누가, 대사)         : 누가 = "N"이면 나레이션
#   ("choice", [(문장, 호감도 변화, 점프할 라벨), ...])
#   ("jump", 라벨)
#   ("if", 기준, 이상일 때 라벨, 미만일 때 라벨) : 호감도로 갈림길
#   ("ending",)                : 호감도로 엔딩 결정
#   ("end", 엔딩 이름)
# =========================================================
SCRIPT = [
    ("label", "start"),
    ("bg", "campus"),
    ("say", "N", "11월의 마지막 주. 캠퍼스에는 벌써 찬 바람이 분다."),
    ("say", "N", "다음 주면 학교 축제, 그리고 곧 기말고사."),
    ("say", "N", "나는 사진 동아리 2학년. 찍는 건 좋아하지만, 사람한테 말 거는 건 영 서툴다."),
    ("say", "N", "...그리고 나는 아직, 같은 과 동기 서리와 제대로 이야기해 본 적이 없다."),

    ("bg", "classroom"),
    ("say", "N", "1교시 전공 수업. 오늘따라 강의실이 북적인다."),
    ("show", "seori"),
    ("say", "N", "남은 자리는 하나. 서리의 옆자리뿐이다."),
    ("say", "me", "저기... 여기 앉아도 돼?"),
    ("say", "seori", "...응. 비어 있어."),
    ("say", "N", "수업이 시작되자, 서리가 가방을 한참 뒤적인다."),
    ("say", "seori", "...펜을 안 가져왔네."),
    ("choice", [("내 펜을 빌려준다", 1, "c1_pen"),
                ("모른 척 수업을 듣는다", -1, "c1_ignore"),
                ("필기를 대신 해 준다고 한다", 2, "c1_note")]),

    ("label", "c1_pen"),
    ("say", "me", "이거 써. 나 하나 더 있어."),
    ("say", "seori", "...고마워. 끝나고 돌려줄게."),
    ("jump", "c1_end"),
    ("label", "c1_ignore"),
    ("say", "N", "...괜히 말을 걸기가 어색하다."),
    ("say", "N", "서리는 결국 휴대폰으로 칠판을 찍기 시작했다."),
    ("jump", "c1_end"),
    ("label", "c1_note"),
    ("say", "me", "필기는 내가 할 테니까, 끝나고 사진 찍어 가."),
    ("say", "seori", "...정말? 그럼 부탁할게."),
    ("say", "N", "서리가 아주 살짝 웃은 것 같았다."),
    ("label", "c1_end"),

    ("hide",),
    ("bg", "cafeteria"),
    ("say", "N", "점심시간, 학생식당."),
    ("show", "yeoreum"),
    ("say", "yeoreum", "야! 여기 여기! 자리 맡아 놨어!"),
    ("say", "N", "같은 동아리 여름이다. 시끄럽지만 미워할 수 없는 녀석."),
    ("say", "yeoreum", "근데 아까 너 서리 옆에 앉았지? 다 봤다~"),
    ("say", "me", "그냥 자리가 거기밖에 없었어."),
    ("say", "yeoreum", "흐응~ 그래? 저기 서리 혼자 밥 먹는데?"),
    ("choice", [("서리에게 같이 먹자고 한다", 1, "c2_invite"),
                ("여름이랑 둘이 먹는다", 0, "c2_alone")]),

    ("label", "c2_invite"),
    ("hide",),
    ("show", "seori"),
    ("say", "me", "서리야, 혹시 같이 먹을래?"),
    ("say", "seori", "...나랑? 여름이는 괜찮아?"),
    ("show", "yeoreum"),
    ("say", "yeoreum", "당연하지! 밥은 여럿이 먹어야 맛있어!"),
    ("show", "seori"),
    ("say", "seori", "...그럼, 실례할게."),
    ("say", "N", "셋이 앉은 테이블은 생각보다 시끌벅적했다."),
    ("jump", "c2_end"),
    ("label", "c2_alone"),
    ("say", "me", "아냐, 오늘은 그냥 우리끼리 먹자."),
    ("say", "yeoreum", "에이, 재미없게."),
    ("say", "N", "고개를 돌리니, 서리는 벌써 식판을 들고 일어나고 있었다."),
    ("label", "c2_end"),

    ("hide",),
    ("bg", "library"),
    ("say", "N", "오후, 도서관 3층. 기말 과제 자료를 찾으러 왔다."),
    ("show", "seori"),
    ("say", "N", "창가 자리에 서리가 앉아 있다. 펼쳐 둔 건 전공책이 아니라 사진집이다."),
    ("say", "seori", "...아. 안녕."),
    ("say", "me", "그거 사진집이야?"),
    ("say", "seori", "응. 겨울 사진만 모아 둔 거야. 눈 내린 거리 같은 거."),
    ("choice", [("사진 찍는 거 좋아해?", 2, "c3_photo"),
                ("과제는 안 해?", -1, "c3_work"),
                ("겨울은 추워서 별로던데", -1, "c3_cold")]),

    ("label", "c3_photo"),
    ("say", "seori", "...응. 좋아해. 특히 첫눈 오는 날."),
    ("say", "seori", "매년 첫눈을 찍으려고 하는데, 늘 놓쳐."),
    ("say", "me", "다음엔 같이 찍으러 가자. 나 사진 동아리거든."),
    ("say", "seori", "...그래. 기억해 둘게."),
    ("jump", "c3_end"),
    ("label", "c3_work"),
    ("say", "seori", "...하고 있었어. 잠깐 쉬는 중이었어."),
    ("say", "N", "서리가 사진집을 조용히 덮었다."),
    ("jump", "c3_end"),
    ("label", "c3_cold"),
    ("say", "seori", "...그렇구나."),
    ("say", "N", "대화가 거기서 끊겼다. 괜한 말을 한 것 같다."),
    ("label", "c3_end"),

    ("hide",),
    ("bg", "clubroom"),
    ("say", "N", "며칠 뒤, 사진 동아리방."),
    ("show", "eunbit"),
    ("say", "eunbit", "안녕하세요! 학생회 은빛이에요."),
    ("say", "eunbit", "이번 축제 기록 사진을 사진 동아리에 부탁드리려고 왔어요."),
    ("say", "eunbit", "마지막 날 밤에 찍어 줄 사람이 두 명 필요한데, 한 명은 동아리 밖에서 데려와도 돼요."),
    ("show", "yeoreum"),
    ("say", "yeoreum", "오, 그럼 네가 해! 그리고 나머지 한 명은... 알지?"),
    ("choice", [("서리에게 연락한다", 1, "c4_seori"),
                ("여름에게 같이 하자고 한다", -1, "c4_yeoreum")]),

    ("label", "c4_seori"),
    ("say", "N", "떨리는 손으로 메시지를 보냈다."),
    ("say", "N", "'축제 마지막 날, 같이 사진 찍을래?'"),
    ("say", "N", "...답장은 5분 뒤에 왔다."),
    ("show", "seori"),
    ("say", "seori", "'좋아. 카메라는 내가 챙겨 갈게.'"),
    ("jump", "c4_end"),
    ("label", "c4_yeoreum"),
    ("say", "yeoreum", "엥, 나? 나 그날 밴드 공연 있는데..."),
    ("say", "yeoreum", "...뭐, 그럼 서리한테는 내가 말해 볼게."),
    ("say", "N", "그렇게 해서 결국, 셋이 같이 하게 되었다."),
    ("label", "c4_end"),

    ("hide",),
    ("bg", "campus"),
    ("say", "N", "주말 오후. 축제 전에 카메라 연습을 하자며 동아리 사람들이 호숫가에 모였다."),
    ("show", "yeoreum"),
    ("say", "yeoreum", "자자, 오늘의 주제는 '가을의 끝'! 각자 마음에 드는 걸 찍어 오기!"),
    ("say", "N", "여름은 그렇게 외치고는 낙엽 더미로 뛰어들었다."),
    ("show", "seori"),
    ("say", "seori", "...나도 와도 되는 거였어? 동아리 사람도 아닌데."),
    ("say", "me", "축제 때 같이 찍을 거니까, 미리 연습하는 거지."),
    ("say", "N", "서리는 오래된 필름 카메라를 들고 있었다."),
    ("say", "seori", "아빠가 쓰던 거야. 디지털보다 느리지만, 난 이게 좋아."),
    ("say", "N", "한참을 걷던 서리가 호숫가에서 멈춰 섰다. 물 위에 낙엽이 떠 있다."),
    ("say", "seori", "...여기, 좋다."),
    ("choice", [("서리를 찍는다", 1, "c7_shoot"),
                ("옆에서 같은 풍경을 찍는다", 2, "c7_same"),
                ("여름 쪽으로 가 본다", -1, "c7_leave")]),

    ("label", "c7_shoot"),
    ("say", "N", "셔터 소리에 서리가 돌아봤다."),
    ("say", "seori", "...지금 나 찍었어?"),
    ("say", "me", "풍경이랑 잘 어울려서."),
    ("say", "seori", "...나중에 보여 줘. 이상하게 나왔으면 지울 거야."),
    ("jump", "c7_end"),
    ("label", "c7_same"),
    ("say", "N", "말없이 서리 옆에 서서, 같은 호수를 찍었다."),
    ("say", "seori", "...같은 걸 찍어도, 사진은 다르게 나오겠지."),
    ("say", "seori", "나중에 서로 바꿔서 보자."),
    ("jump", "c7_end"),
    ("label", "c7_leave"),
    ("show", "yeoreum"),
    ("say", "yeoreum", "야, 이것 좀 봐! 오리 엄청 많아!"),
    ("say", "N", "여름에게 끌려다니다 돌아오니, 서리는 혼자 호숫가에 앉아 있었다."),
    ("label", "c7_end"),

    ("hide",),
    ("if", 5, "eve_high", "eve_low"),           # 지금까지의 호감도로 갈림길

    ("label", "eve_high"),
    ("say", "N", "축제 전날 밤, 서리에게서 메시지가 왔다."),
    ("show", "seori"),
    ("say", "seori", "'일기예보 보니까... 내일 첫눈 올지도 모른대.'"),
    ("say", "seori", "'혹시 오면, 같이 찍어 줄래?'"),
    ("say", "me", "'당연하지.'"),
    ("jump", "eve_end"),
    ("label", "eve_low"),
    ("say", "N", "축제 전날 밤. 휴대폰은 조용하다."),
    ("say", "N", "서리는 내일 와 줄까."),
    ("label", "eve_end"),

    ("hide",),
    ("bg", "festival"),
    ("say", "N", "축제 마지막 날 밤. 운동장은 조명과 사람들로 가득하다."),
    ("show", "eunbit"),
    ("say", "eunbit", "와 주셨네요! 무대 쪽이랑 부스 쪽 나눠서 찍어 주시면 돼요."),
    ("say", "N", "무대에서는 여름의 밴드가 공연 중이다."),
    ("show", "yeoreum"),
    ("say", "yeoreum", "다들 소리 질러어어! 사진 동아리, 나 예쁘게 찍어라!"),
    ("show", "seori"),
    ("say", "seori", "...왔어. 사람 진짜 많네."),
    ("say", "N", "서리는 목도리를 코끝까지 올리고 있었다."),
    ("choice", [("내 핫팩을 건넨다", 1, "c5_pack"),
                ("추우면 들어가 있으라고 한다", -1, "c5_cold"),
                ("목도리가 잘 어울린다고 한다", 1, "c5_scarf")]),

    ("label", "c5_pack"),
    ("say", "seori", "...따뜻하다. 너는 괜찮아?"),
    ("say", "me", "난 하나 더 있어."),
    ("say", "seori", "준비성 좋네. 원래 그렇게 챙겨 다녀?"),
    ("say", "N", "서리가 처음으로 소리 내어 웃었다."),
    ("jump", "c5_end"),
    ("label", "c5_cold"),
    ("say", "seori", "...아니야. 찍기로 했으니까."),
    ("say", "N", "걱정돼서 한 말인데, 괜히 퉁명스럽게 나와 버렸다."),
    ("jump", "c5_end"),
    ("label", "c5_scarf"),
    ("say", "seori", "...이거? 엄마가 떠 준 거야."),
    ("say", "seori", "칭찬받으니까... 좀 쑥스럽네."),
    ("label", "c5_end"),

    ("say", "N", "한참 사진을 찍다 보니, 마지막 순서인 불꽃놀이 시간이 다가왔다."),
    ("say", "seori", "...잠깐 쉬었다 하자. 저기, 운동장 끝 벤치."),
    ("say", "N", "둘이서 벤치에 앉았다. 멀리서 음악 소리가 들린다."),
    ("say", "seori", "있잖아. 내가 왜 첫눈을 찍고 싶은지 말한 적 없지?"),
    ("say", "seori", "어릴 때, 첫눈 오는 날 같이 사진 찍자고 약속한 친구가 있었어."),
    ("say", "seori", "그 애가 전학 가고 나서는... 혼자 찍는 게 좀 쓸쓸해서."),
    ("choice", [("올해는 내가 같이 찍을게", 2, "c6_promise"),
                ("그 친구한테 연락해 봐", 0, "c6_friend"),
                ("말없이 끝까지 들어 준다", 1, "c6_listen")]),

    ("label", "c6_promise"),
    ("say", "seori", "...진짜?"),
    ("say", "me", "응. 첫눈 오면, 나한테 제일 먼저 연락해."),
    ("jump", "c6_end"),
    ("label", "c6_friend"),
    ("say", "seori", "...그럴까. 연락이 끊긴 지 너무 오래돼서."),
    ("say", "N", "서리는 쓸쓸하게 웃었다."),
    ("jump", "c6_end"),
    ("label", "c6_listen"),
    ("say", "N", "아무 말도 하지 않았다. 그냥, 서리가 끝까지 말할 수 있게."),
    ("say", "seori", "...들어 줘서 고마워."),
    ("label", "c6_end"),

    ("say", "N", "그때, 첫 불꽃이 하늘로 솟아올랐다."),
    ("ending",),

    # ---------------- 엔딩 ----------------
    ("label", "end_good"),
    ("hide",),
    ("bg", "snow"),
    ("say", "N", "불꽃이 터지는 하늘 사이로, 하얀 것이 천천히 내려온다."),
    ("show", "seori"),
    ("say", "seori", "...눈이다."),
    ("say", "seori", "첫눈이야!"),
    ("say", "N", "서리가 카메라를 들다가, 멈추고 나를 바라본다."),
    ("say", "seori", "...오늘은 사진보다, 그냥 같이 보고 싶어."),
    ("say", "seori", "내년에도, 그 다음 해에도... 첫눈은 너랑 볼래."),
    ("end", "첫눈 엔딩"),

    ("label", "end_normal"),
    ("say", "N", "불꽃놀이가 끝나고, 우리는 찍은 사진을 나눠 보았다."),
    ("show", "seori"),
    ("say", "seori", "오늘 즐거웠어. 고마워."),
    ("say", "seori", "...좋은 친구가 생긴 것 같아."),
    ("say", "N", "첫눈은 오지 않았다. 하지만 언젠가는, 같이 볼 수 있을지도 모른다."),
    ("end", "친구 엔딩"),

    ("label", "end_bad"),
    ("say", "N", "불꽃놀이가 끝나자, 서리는 말없이 카메라를 챙겼다."),
    ("show", "seori"),
    ("say", "seori", "...수고했어. 사진은 은빛이한테 보낼게."),
    ("hide",),
    ("say", "N", "서리의 뒷모습이 인파 속으로 사라졌다."),
    ("say", "N", "그해 첫눈은, 기숙사 창문으로 혼자 보았다."),
    ("end", "쓸쓸한 엔딩"),
]

# 라벨 이름 → 시나리오 몇 번째 줄인지 (시작할 때 한 번 계산)
LABELS = {cmd[1]: i for i, cmd in enumerate(SCRIPT) if cmd[0] == "label"}

GOOD_LINE = 8       # 호감도 이 이상이면 첫눈 엔딩
NORMAL_LINE = 4     # 이 이상이면 친구 엔딩, 미만이면 쓸쓸한 엔딩

# =========================================================
# 5. 게임 상태
# =========================================================
s = {}

def new_game():
    s.update({
        "scene": "story",     # title / story / ending
        "pc": 0,              # 지금 읽고 있는 시나리오 줄 번호
        "bg": "campus",
        "portrait": None,
        "mode": "say",        # say / choice
        "speaker": "N",
        "text": "",
        "shown": 0,
        "choices": [],
        "cursor": 0,
        "love": 0,            # 호감도
        "popup": 0,           # 호감도 변화 표시 (+1, -1 ...)
        "popup_t": 0,         # 표시 남은 프레임
        "ending": "",
    })
    run_script()

def run_script():
    """대사나 선택지가 나올 때까지 시나리오 명령을 차례로 실행"""
    while True:
        cmd = SCRIPT[s["pc"]]
        kind = cmd[0]
        s["pc"] += 1

        if kind == "label":
            continue
        elif kind == "bg":
            s["bg"] = cmd[1]
        elif kind == "show":
            s["portrait"] = cmd[1]
        elif kind == "hide":
            s["portrait"] = None
        elif kind == "jump":
            s["pc"] = LABELS[cmd[1]]
        elif kind == "if":
            target = cmd[2] if s["love"] >= cmd[1] else cmd[3]
            s["pc"] = LABELS[target]
        elif kind == "ending":
            if s["love"] >= GOOD_LINE:
                s["pc"] = LABELS["end_good"]
            elif s["love"] >= NORMAL_LINE:
                s["pc"] = LABELS["end_normal"]
            else:
                s["pc"] = LABELS["end_bad"]
        elif kind == "say":
            s["mode"] = "say"
            s["speaker"], s["text"] = cmd[1], cmd[2]
            s["shown"] = 0
            return
        elif kind == "choice":
            s["mode"] = "choice"
            s["choices"] = cmd[1]
            s["cursor"] = 0
            return
        elif kind == "end":
            s["scene"] = "ending"
            s["ending"] = cmd[1]
            return

def choose():
    text, delta, label = s["choices"][s["cursor"]]
    s["love"] += delta
    if delta != 0:
        s["popup"] = delta
        s["popup_t"] = 45
    s["pc"] = LABELS[label]
    run_script()

# =========================================================
# 6. 그리기
# =========================================================
def wrap(text, font, max_w):
    lines, cur = [], ""
    for word in text.split(" "):
        test = word if cur == "" else cur + " " + word
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines

def center_text(y, text, font, color):
    w = draw.textlength(text, font=font)
    draw.text(((W - w) // 2, y), text, font=font, fill=color)

def draw_heart(x, y, color):
    draw.ellipse((x, y, x + 8, y + 8), fill=color)
    draw.ellipse((x + 7, y, x + 15, y + 8), fill=color)
    draw.polygon([(x, y + 5), (x + 15, y + 5), (x + 7, y + 14)], fill=color)

def draw_background():
    place, bg = BACKGROUNDS[s["bg"]]
    img.paste(bg, (0, 0))
    if s["bg"] == "snow":
        draw_snow()
    if place:
        w = draw.textlength(place, font=SMALL)
        draw.rectangle((0, 0, w + 10, 16), fill=(0, 0, 0))
        draw.text((5, 2), place, font=SMALL, fill=(230, 230, 230))

def draw_story():
    draw_background()
    if s["portrait"]:
        pic = PORTRAIT[s["portrait"]]
        img.paste(pic, (45, 4), pic)

    draw.rectangle((6, 148, 233, 233), fill=(15, 12, 25), outline=(200, 170, 200), width=2)

    if s["mode"] == "say":
        y = 176
        if s["speaker"] == "N":                     # 나레이션: 이름 없이
            y = 160
            color = (215, 215, 225)
        else:
            name, name_color = SPEAKERS[s["speaker"]]
            draw.text((16, 154), name, font=FONT, fill=name_color)
            color = (255, 255, 255)
        left = s["shown"]
        for i, line in enumerate(wrap(s["text"], FONT, 208)):
            if left <= 0:
                break
            draw.text((16, y + i * 19), line[:left], font=FONT, fill=color)
            left -= len(line) + 1
        if s["shown"] >= len(s["text"]) and (frame // 15) % 2 == 0:
            draw.polygon([(218, 221), (226, 221), (222, 226)], fill=(255, 255, 255))

    else:                                            # 선택지
        for i, (text, delta, label) in enumerate(s["choices"]):
            y = 156 + i * 25
            if i == s["cursor"]:
                draw.rectangle((12, y - 2, 227, y + 20), fill=(70, 55, 100))
                draw.polygon([(16, y + 3), (16, y + 15), (24, y + 9)], fill=(255, 200, 230))
                color = (255, 255, 255)
            else:
                color = (170, 165, 185)
            draw.text((30, y + 1), text, font=FONT, fill=color)

    if s["popup_t"] > 0:                             # 호감도 변화 표시
        rise = (45 - s["popup_t"]) // 3
        y = 24 - rise
        if s["popup"] > 0:
            draw_heart(184, y, (255, 110, 150))
            draw.text((203, y), "+" + str(s["popup"]), font=FONT, fill=(255, 150, 180))
        else:
            draw_heart(184, y, (130, 130, 150))
            draw.text((203, y), str(s["popup"]), font=FONT, fill=(170, 170, 190))

    if show_love:                                    # B 버튼: 연습용 호감도 보기
        draw.rectangle((170, 128, 233, 145), fill=(0, 0, 0))
        draw.text((176, 130), "호감도 " + str(s["love"]), font=SMALL, fill=(255, 180, 200))

def draw_title():
    img.paste(BACKGROUNDS["snow"][1], (0, 0))
    draw_snow()
    pic = PORTRAIT["seori"]
    img.paste(pic, (45, 40), pic)
    draw.rectangle((0, 18, W - 1, 62), fill=(20, 25, 55))
    center_text(22, "첫눈이 오면", BIG, (235, 240, 255))
    if (frame // 15) % 2 == 0:
        draw.rectangle((50, 200, 189, 222), fill=(20, 25, 55))
        center_text(203, "A 버튼을 눌러 시작", FONT, (255, 255, 255))

def draw_ending():
    draw_background()
    draw.rectangle((20, 60, 219, 180), fill=(10, 10, 25), outline=(200, 170, 200), width=2)
    center_text(75, "END", SMALL, (180, 180, 200))
    center_text(95, s["ending"], BIG, (255, 220, 235))
    center_text(135, "최종 호감도  " + str(s["love"]), FONT, (255, 180, 200))
    center_text(158, "A: 타이틀로", SMALL, (220, 220, 230))

def render():
    if s["scene"] == "title":
        draw_title()
    elif s["scene"] == "story":
        draw_story()
    elif s["scene"] == "ending":
        draw_ending()
    disp.image(img)

# =========================================================
# 7. 입력 처리
# =========================================================
def handle(name):
    global show_love
    if name == "B":
        show_love = not show_love
        return

    if s["scene"] == "title":
        if name == "A":
            new_game()

    elif s["scene"] == "story":
        if s["mode"] == "say":
            if name == "A":
                if s["shown"] < len(s["text"]):
                    s["shown"] = len(s["text"])     # 타이핑 중이면 한 번에 다 보이기
                else:
                    run_script()                    # 다음 명령으로
        else:
            if name == "UP":
                s["cursor"] = (s["cursor"] - 1) % len(s["choices"])
            elif name == "DOWN":
                s["cursor"] = (s["cursor"] + 1) % len(s["choices"])
            elif name == "A":
                choose()

    elif s["scene"] == "ending":
        if name == "A":
            s["scene"] = "title"

# =========================================================
# 8. 메인 루프
# =========================================================
frame = 0
show_love = False
s["scene"] = "title"

try:
    while True:
        pressed = read_just_pressed()
        for name in pressed:
            handle(name)

        dirty = len(pressed) > 0
        scene = s["scene"]

        if scene == "story" and s["mode"] == "say" and s["shown"] < len(s["text"]):
            s["shown"] += 1                      # 타자기 효과
            dirty = True
        if scene == "story" and s["popup_t"] > 0:
            s["popup_t"] -= 1
            dirty = True
        if scene == "title" or s.get("bg") == "snow":
            update_snow()                        # 눈 내리는 장면은 매 프레임 갱신
            dirty = True
        if frame % 15 == 0:
            dirty = True                         # 깜빡이는 표시
        if dirty:
            render()

        frame += 1
        time.sleep(1 / FPS)
except KeyboardInterrupt:
    pass
finally:
    disp.image(Image.new("RGB", (W, H)))
    backlight.value = False
