import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import config

# Configurable parameters
OLED_WIDTH = getattr(config, 'oled_width', 128)
OLED_HEIGHT = getattr(config, 'oled_height', 64)
OLED_I2C_ADDRESS = getattr(config, 'oled_i2c_address', 0x3C)
I2C_FREQ = getattr(config, 'i2c_frequency', None)

# Initialize I2C and display
print("Initializing I2C and OLED display...")
if I2C_FREQ:
    i2c = busio.I2C(board.SCL, board.SDA, frequency=I2C_FREQ)
else:
    i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=OLED_I2C_ADDRESS)
display.fill(0)
display.show()

# Create blank image for drawing
image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# Draw test pattern
for i in range(3):
    draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), outline=0, fill=0)
    draw.text((0, 0), "OLED Test", font=font, fill=255)
    draw.text((0, 16), f"Line {i+1}", font=font, fill=255)
    draw.text((0, 32), "Hello, World!", font=font, fill=255)
    display.image(image)
    display.show()
    print(f"Displayed test pattern {i+1}")
    time.sleep(2)
    draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), outline=0, fill=0)
    display.image(image)
    display.show()
    time.sleep(0.5)

print("OLED test complete.")
