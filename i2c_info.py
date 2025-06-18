import os
import sys

def get_rpi_i2c_baudrate():
    """Try to read the I2C baudrate from /boot/config.txt (Raspberry Pi only)."""
    config_path = '/boot/config.txt'
    baudrate = None
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                if line.strip().startswith('dtparam=i2c_arm_baudrate='):
                    try:
                        baudrate = int(line.strip().split('=')[1])
                    except Exception:
                        pass
    return baudrate

def main():
    print("I2C Bus Information (Linux/Raspberry Pi):\n")
    # Try to get baudrate from /boot/config.txt
    baudrate = get_rpi_i2c_baudrate()
    if baudrate:
        print(f"Configured I2C baudrate in /boot/config.txt: {baudrate} Hz")
    else:
        print("No explicit I2C baudrate found in /boot/config.txt (using OS default, usually 100000 Hz)")
    # Show detected I2C devices
    print("\nDetected I2C devices (using i2cdetect):")
    try:
        os.system('i2cdetect -y 1')
    except Exception as e:
        print(f"Could not run i2cdetect: {e}")

if __name__ == "__main__":
    main()
