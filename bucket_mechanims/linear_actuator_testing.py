# dependency to install : pip3 install pyserial

import serial
import time

# SETTINGS
# Use '/dev/ttyTHS0' for J41 Header Pins (8 & 10) 
# Use '/dev/ttyACM0' or '/dev/ttyUSB0' if using a USB cable
SERIAL_PORT = "/dev/ttyTHS0" 
BAUDRATE = 115200

try:
    # Initialize connection
    stm32 = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    time.sleep(2) # Wait for STM32 to reset after connection
    print(f"Successfully connected to {SERIAL_PORT}")
except Exception as e:
    print(f"FATAL ERROR: Could not open serial port: {e}")
    exit()

def send_command(cmd_char, duration=0):
    """Sends a command and optionally waits/stops"""
    print(f"Action: {cmd_char} for {duration}s")
    stm32.write(cmd_char.encode()) # Sends 'U', 'D', or 'S'
    
    if duration > 0:
        time.sleep(duration)
        stm32.write(b'S') # Automatic safety stop
        print("Safety Stop Sent.")

# --- AUTONOMOUS SEQUENCE ---
try:
    # 1. Extend (Up)
    send_command('U', duration=4)
    
    # 2. Cool-down / Rest (Crucial for 10% Duty Cycle)
    print("Resting motor...")
    time.sleep(2)
    
    # 3. Retract (Down)
    send_command('D', duration=4)

except KeyboardInterrupt:
    print("\n[!] Emergency Stop Triggered by User")
    stm32.write(b'S')
finally:
    stm32.close()
    print("Serial port closed.")