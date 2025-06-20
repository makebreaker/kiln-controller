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

temp = 0
while(True):
    time.sleep(1)
    try:
        tc_type = getattr(config, 'thermocouple_type', 'K')
        print(f"Thermocouple type: {tc_type}")
        temp = sensor.temperature
        scale = "C"
        if config.temp_scale == "f":
            temp = temp * (9/5) + 32 
            scale ="F"
        if is_mcp9600:
            # Print all available MCP9600 diagnostics/state
            try:
                print(f"Temperature: {temp:.2f}{scale}")
                print(f"Ambient (cold junction) temp: {sensor.ambient_temperature:.2f}C")
                print(f"Delta temp: {sensor.delta_temperature:.2f}C")
                # print(f"ADC value: {sensor.adc_value}")
                print(f"Thermocouple type (chip): {getattr(sensor, 'thermocouple_type', 'N/A')}")
                print(f"Status: {getattr(sensor, 'status', 'N/A')}")
                print(f"Alert 1: {getattr(sensor, 'alert_1', 'N/A')}")
                print(f"Alert 2: {getattr(sensor, 'alert_2', 'N/A')}")
                print(f"Alert 3: {getattr(sensor, 'alert_3', 'N/A')}")
                print(f"Alert 4: {getattr(sensor, 'alert_4', 'N/A')}")
            except Exception as diagerr:
                print(f"MCP9600 diagnostics error: {diagerr}")
        else:
            print("%s %0.2f%s" %(datetime.datetime.now(),temp,scale))
    except Exception as error:
        print("error: " , error)
