from PIL import ImageFont
from scenes.scene import Scene
from scenes.play_scene import PlayScene
from stages import STAGES
from settings import W, H, FONT_PATH, BOLD_FONT_PATH

TITLE_FONT = ImageFont.truetype(BOLD_FONT_PATH, 26)
MENU_FONT = ImageFont.truetype(BOLD_FONT_PATH, 26)

class StageSelectScene(Scene):
    STAGENUM = ["I", "II", "III", "IV", "V", "EX"]

    def __init__(self):
        self.selected_stage = 0

    def handle(self, name):
        if name == "LEFT":
            self.selected_stage = (self.selected_stage - 1) % len(self.STAGENUM) 
        elif name == "RIGHT":
            self.selected_stage = (self.selected_stage + 1) % len(self.STAGENUM)
        elif name == "DOWN":
            self.selected_stage = (self.selected_stage + 3) % len(self.STAGENUM)
        elif name == "UP":
            self.selected_stage = (self.selected_stage - 3) % len(self.STAGENUM)
        elif name == "A":
            return PlayScene(self.selected_stage)
        elif name == "B":
            from scenes.title_scene import TitleScene
            return TitleScene()
        return self

    def draw(self, img, pen):
        pen.rectangle((0, 0, W - 1, H - 1), fill=(20, 15, 30))
        pen.text((W // 2, 40), "스테이지 선택", font=TITLE_FONT, anchor="mm", fill=(255, 255, 255))

        for i in range(len(self.STAGENUM)):
            row, col = i // 3, i % 3
            cx = 50 + col * 70
            cy = 110 + row * 75

            if self.STAGENUM[i] == "EX":
                box_color = (230, 120, 170)
            else:
                box_color = (60, 50, 80)

            if i == self.selected_stage:
                line_color = (255, 220, 120)
            else:
                line_color = (90, 80, 110)

            pen.rectangle((cx - 30, cy - 30, cx + 30, cy + 30), fill = box_color, outline = line_color, width = 3)
            pen.text((cx, cy), self.STAGENUM[i], font=MENU_FONT, anchor="mm", fill=(255, 255, 255))