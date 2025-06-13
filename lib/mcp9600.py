# MCP9600 Thermocouple Support
# This file provides a class for using the MCP9600 thermocouple amplifier with CircuitPython
import adafruit_mcp9600
import board
import busio
import time

class MCP9600:
    def __init__(self, i2c_bus=None, address=0x67):
        if i2c_bus is None:
            i2c_bus = busio.I2C(board.SCL, board.SDA)
        self.mcp = adafruit_mcp9600.MCP9600(i2c_bus, address=address)

    def temperature(self):
        return self.mcp.temperature

    def ambient_temperature(self):
        return self.mcp.ambient_temperature

    def shutdown(self):
        self.mcp.shutdown = True

    def wake(self):
        self.mcp.shutdown = False
