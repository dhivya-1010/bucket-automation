import serial
import time

SERIAL_PORT = "/dev/ttyTHS1"
BAUDRATE = 115200

stm = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)

def send(cmd, wait=3):
    print("Jetson -> STM:", cmd)
    stm.write((cmd + "\n").encode())
    time.sleep(wait)

try:
    # Bucket dig forward (worm gear ON)
    send("DIG_START", 3)

    # Stop (important – worm gear self-lock)
    send("STOP", 2)

    # Reverse (ONLY if STM supports reverse)
    send("DIG_REVERSE", 3)

    # Final stop
    send("STOP", 2)

except KeyboardInterrupt:
    send("STOP")

finally:
    stm.close()
