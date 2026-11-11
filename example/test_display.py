import time
import board, digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7789

cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
rst_pin = digitalio.DigitalInOut(board.D24)

backlight = digitalio.DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True

spi = board.SPI()
disp = st7789.ST7789(
    spi, width=240, height=240, rotation=180, y_offset=80,
    cs=cs_pin, dc=dc_pin, rst=rst_pin, baudrate=24000000,
)

img = Image.new("RGB", (disp.width, disp.height))
draw = ImageDraw.Draw(img)
for color in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]:
    draw.rectangle((0, 0, 239, 239), fill=color)
    disp.image(img)
    print("color", color)
    time.sleep(0.6)

draw.rectangle((0, 0, 239, 239), fill=(0, 0, 0))
draw.text((20, 110), "READY", fill=(0, 255, 0))
disp.image(img)
print("done")
