# dependency to install : pip3 install pyserial

import serial
import time

# Change port if needed
SERIAL_PORT = "/dev/ttyUSB0"   # or /dev/ttyTHS1
BAUDRATE = 115200

stm = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)

def send(cmd):
    print("Sending:", cmd)
    stm.write((cmd + "\n").encode())
    time.sleep(0.1)

try:
    # EXTEND
    send("ACT_EXTEND")
    time.sleep(4)   # full stroke ~4 sec

    send("ACT_STOP")
    time.sleep(5)   # REST (important)

    # RETRACT
    send("ACT_RETRACT")
    time.sleep(4)

    send("ACT_STOP")

except KeyboardInterrupt:
    send("ACT_STOP")

finally:
    stm.close()
