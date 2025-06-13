import time

import board
import busio

import adafruit_mcp9600

try:
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    mcp = adafruit_mcp9600.MCP9600(i2c)
except Exception as e:
    print("Failed to initialize MCP9600:", e)
    print("Check wiring, power, and I2C address (default 0x60). Run 'i2cdetect -y 1' to verify device is present.")
    exit(1)

while True:
    try:
        print((mcp.ambient_temperature, mcp.temperature, mcp.delta_temperature))
    except Exception as e:
        print("Error reading MCP9600:", e)
    time.sleep(1)