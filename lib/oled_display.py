import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import config

class OledDisplay:
    def __init__(self):
        i2c_freq = getattr(config, 'i2c_frequency', None)
        import board
        import busio
        if i2c_freq:
            i2c = busio.I2C(board.SCL, board.SDA, frequency=i2c_freq)
        else:
            i2c = busio.I2C(board.SCL, board.SDA)
        self.display = adafruit_ssd1306.SSD1306_I2C(
            config.oled_width,
            config.oled_height,
            i2c,
            addr=config.oled_i2c_address
        )
        self.display.fill(0)
        self.display.show()
        self.image = Image.new("1", (config.oled_width, config.oled_height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()

    def update(self, current_temp, target_temp, heater_on):
        self.draw.rectangle((0, 0, config.oled_width, config.oled_height), outline=0, fill=0)
        self.draw.text((0, 0), f"Current: {current_temp:.1f}C", font=self.font, fill=255)
        self.draw.text((0, 16), f"Target:  {target_temp:.1f}C", font=self.font, fill=255)
        self.draw.text((0, 32), f"Heater:  {'ON' if heater_on else 'OFF'}", font=self.font, fill=255)
        self.display.image(self.image)
        self.display.show()
