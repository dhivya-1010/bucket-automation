import serial
import time

# ==============================
# UART CONFIG
# ==============================
SERIAL_PORT = "/dev/ttyTHS1"   # Jetson UART pins
BAUDRATE = 115200

# ==============================
# CONNECT TO STM32
# ==============================
try:
    stm = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    time.sleep(2)  # STM reset wait
    print("[OK] Connected to STM32")
except Exception as e:
    print("[ERROR] UART connection failed:", e)
    exit()

# ==============================
# SEND COMMAND FUNCTION
# ==============================
def send(cmd, wait=2):
    print("Jetson -> STM:", cmd)
    stm.write((cmd + "\n").encode())
    time.sleep(wait)

# ==============================
# WORM GEAR AUTOMATION SEQUENCE
# ==============================
try:
    print("\n[START] Worm gear bucket automation")

    # Start digging (worm gear forward)
    send("DIG_START", 3)

    # Stop motor (important for worm gear)
    send("STOP", 2)

    # Optional reverse (ONLY if STM supports it)
    # send("DIG_REVERSE", 2)
    # send("STOP", 2)

    print("[DONE] Worm gear automation completed")

except KeyboardInterrupt:
    print("\n[EMERGENCY] STOP")
    send("STOP")

finally:
    stm.close()
    print("[INFO] UART closed")
