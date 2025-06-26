#!/usr/bin/env python
import config
from digitalio import DigitalInOut
import time
import datetime
import busio
import adafruit_bitbangio as bitbangio

try:
    import board
except NotImplementedError:
    print("not running a recognized blinka board, exiting...")
    import sys
    sys.exit()

########################################################################
#
# To test your thermocouple...
#
# Edit config.py and set the following in that file to match your
# hardware setup: SPI_SCLK, SPI_MOSI, SPI_MISO, SPI_CS
#
# then run this script...
# 
# ./test-thermocouple.py
#
# It will output a temperature in degrees every second. Touch your
# thermocouple to heat it up and make sure the value changes. Accuracy
# of my thermocouple is .25C.
########################################################################

# spi = None
# if(hasattr(config,'spi_sclk') and
#    hasattr(config,'spi_mosi') and
#    hasattr(config,'spi_miso')):
#     spi = bitbangio.SPI(config.spi_sclk, config.spi_mosi, config.spi_miso)
#     print("Software SPI selected for reading thermocouple")
#     print("SPI configured as:\n")
#     print("    config.spi_sclk = %s BCM pin" % (config.spi_sclk))
#     print("    config.spi_mosi = %s BCM pin" % (config.spi_mosi))
#     print("    config.spi_miso = %s BCM pin" % (config.spi_miso))
#     print("    config.spi_cs   = %s BCM pin\n" % (config.spi_cs))
# else:
#     spi = board.SPI();
#     print("Hardware SPI selected for reading thermocouple")

# cs = DigitalInOut(config.spi_cs)
# cs.switch_to_output(value=True)
# sensor = None

print("\nboard: %s" % (board.board_id))
# if(config.max31855):
#     import adafruit_max31855
#     print("thermocouple: adafruit max31855")
#     sensor = adafruit_max31855.MAX31855(spi, cs)
# if(config.max31856):
#     import adafruit_max31856
#     print("thermocouple: adafruit max31856")
#     tc_type = getattr(config, 'thermocouple_type', 'K')
#     tc_enum = getattr(adafruit_max31856.ThermocoupleType, tc_type)
#     sensor = adafruit_max31856.MAX31856(spi, cs, thermocouple_type=tc_enum)
if(getattr(config, 'mcp9600', 0)):
    import board
    import busio
    import adafruit_mcp9600
    print("thermocouple: adafruit mcp9600")
    i2c_freq = getattr(config, 'i2c_frequency', None)
    if i2c_freq:
        i2c = busio.I2C(board.SCL, board.SDA, frequency=i2c_freq)
    else:
        i2c = busio.I2C(board.SCL, board.SDA)
    address = getattr(config, 'mcp9600_i2c_address', 0x67)
    sensor = adafruit_mcp9600.MCP9600(i2c)
    # Set thermocouple type from config if available
    tc_type = getattr(config, 'thermocouple_type', 'K')
    try:
        sensor.thermocouple_type = tc_type
    except AttributeError:
        pass
    is_mcp9600 = True
else:
    is_mcp9600 = False

print("Degrees displayed in %s\n" % (config.temp_scale))

# Add these to config.py:
# thermocoupleErrorWindow = 0.1  # degrees C
# thermocoupleErrorPeriod = 60   # seconds
try:
    from config import thermocoupleErrorWindow, thermocoupleErrorPeriod
except ImportError:
    thermocoupleErrorWindow = 0.1
    thermocoupleErrorPeriod = 60

# Track temperature history for error detection
from collections import deque

temp_history = deque()
time_history = deque()

temp = 0
consecutive_mcp9600_errors = 0
last_error_check_time = time.time()
while(True):
    time.sleep(1)
    now = time.time()
    try:
        tc_type = getattr(config, 'thermocouple_type', 'K')
        print(f"Thermocouple type: {tc_type}")
        temp = sensor.temperature
        scale = "C"
        mcp9600_fault = False
        # Track temperature and time for error window logic
        temp_c = temp if config.temp_scale.lower() == 'c' else (temp - 32) * 5/9
        temp_history.append(temp_c)
        time_history.append(now)
        # Remove old entries
        while time_history and (now - time_history[0]) > thermocoupleErrorPeriod:
            temp_history.popleft()
            time_history.popleft()
        # Only check if not idle (simulate with a variable, e.g. kiln_running = True)
        kiln_running = True  # Set this to False if you want to simulate idle
        if kiln_running and len(temp_history) > 1:
            temp_min = min(temp_history)
            temp_max = max(temp_history)
            if (temp_max - temp_min) < thermocoupleErrorWindow and (now - time_history[0]) >= thermocoupleErrorPeriod:
                print(f"CRITICAL: Temperature has not changed by more than {thermocoupleErrorWindow}C in {thermocoupleErrorPeriod}s. Halting for safety.")
                break
        if is_mcp9600:
            # Check MCP9600 input range error (bit 0 of status)
            status = getattr(sensor, 'status', 0)
            if status & 0x01:
                print("WARNING: MCP9600 input range error (possible thermocouple disconnect or short)")
                consecutive_mcp9600_errors += 1
                mcp9600_fault = True
            else:
                consecutive_mcp9600_errors = 0
            # Print all available MCP9600 diagnostics/state
            try:
                print(f"Temperature: {temp:.2f}{scale}")
                print(f"Ambient (cold junction) temp: {sensor.ambient_temperature:.2f}C")
                print(f"Delta temp: {sensor.delta_temperature:.2f}C")
                print(f"Thermocouple type (chip): {getattr(sensor, 'thermocouple_type', 'N/A')}")
                print(f"Status: {status}")
                print(f"Alert 1: {getattr(sensor, 'alert_1', 'N/A')}")
                print(f"Alert 2: {getattr(sensor, 'alert_2', 'N/A')}")
                print(f"Alert 3: {getattr(sensor, 'alert_3', 'N/A')}")
                print(f"Alert 4: {getattr(sensor, 'alert_4', 'N/A')}")
            except Exception as diagerr:
                print(f"MCP9600 diagnostics error: {diagerr}")
            if consecutive_mcp9600_errors >= 3:
                print("CRITICAL: Multiple consecutive MCP9600 input range errors detected. Halting for safety.")
                break
        else:
            print("%s %0.2f%s" %(datetime.datetime.now(),temp,scale))
    except Exception as error:
        print("error: " , error)
        if is_mcp9600:
            consecutive_mcp9600_errors += 1
            if consecutive_mcp9600_errors >= 3:
                print("CRITICAL: Multiple consecutive MCP9600 errors detected. Halting for safety.")
                break
