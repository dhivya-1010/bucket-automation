# dependency to install : pip3 install pyserial

import serial
import time

# ==============================
# UART CONFIG (Jetson)
# ==============================
SERIAL_PORT = "/dev/ttyTHS1"   # Jetson UART pins
BAUDRATE = 115200

# ==============================
# OPEN SERIAL
# ==============================
try:
    uart = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    time.sleep(2)   # STM reset wait
    print("UART connected")
except Exception as e:
    print("UART error:", e)
    exit()

# ==============================
# SEND ONLY (OUTPUT)
# ==============================
try:
    while True:
        cmd = input("Type command to send: ")
        uart.write((cmd + "\n").encode())
        print("Sent:", cmd)

except KeyboardInterrupt:
    print("\nStopped by user")

finally:
    uart.close()
    print("UART closed")
