import sys

from scenes.scene import Scene
from scenes.play_scene import PlayScene
from PIL import ImageFont
from scenes.stage_select_scene import StageSelectScene
from settings import W, H, FONT_PATH, BOLD_FONT_PATH

TITLE_FONT = ImageFont.truetype(BOLD_FONT_PATH, 26)
MENU_FONT = ImageFont.truetype(FONT_PATH, 20)

# 메인 메뉴, 타이틀 스크린

class TitleScene(Scene):
    def __init__(self):
        self.MENU = ["처음부터", "스테이지 선택", "게임 종료"]
        self.selected_menu = 0
         
    def handle(self, name):
        if name == "UP":
            self.selected_menu = (self.selected_menu - 1) % len(self.MENU)
        elif name == "DOWN":
            self.selected_menu = (self.selected_menu + 1) % len(self.MENU)
        elif name == "A":
            if self.selected_menu == 0:
                return PlayScene(0)
            elif self.selected_menu == 1:
                return StageSelectScene()
            elif self.selected_menu == 2:
                sys.exit()
             
        return self

    def draw(self, img, pen):
        # 배경 칠하기
        pen.rectangle((0, 0, W - 1, H - 1), fill=(20, 15, 30))
        pen.text((W // 2, 70), "핑크 엘프양 찾기", font=TITLE_FONT, anchor="mm", fill=(255, 190, 220))

        for i in range(len(self.MENU)):
            item = self.MENU[i]
            y = 140 + i * 30
            if i == self.selected_menu:
                width = pen.textlength(item, font=MENU_FONT)

                lx = W // 2 - width // 2 - 16
                rx = W // 2 + width // 2 + 16

                pen.polygon([(lx, y - 6), (lx, y + 6), (lx + 8, y)], fill=(255, 220, 120))
                pen.polygon([(rx, y - 6), (rx, y + 6), (rx - 8, y)], fill=(255, 220, 120))

                color = (255, 220, 120)
            else:
                color = (130, 120, 150)
            pen.text((W // 2, y), item, font=MENU_FONT, anchor="mm", fill=color)