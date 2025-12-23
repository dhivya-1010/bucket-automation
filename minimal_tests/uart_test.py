import serial
import time

SERIAL_PORT = "/dev/ttyTHS1"
BAUDRATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)

while True:
    cmd = input("Type command (DIG_START / DUMP / RESET): ")
    ser.write((cmd + "\n").encode())
