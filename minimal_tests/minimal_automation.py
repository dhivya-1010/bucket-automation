# without cam reading
import serial
import time
from enum import Enum

# ==============================
# CONFIGURATION
# ==============================
SERIAL_PORT = "/dev/ttyTHS1"
BAUDRATE = 115200
MAX_DIG_RETRIES = 2

# ==============================
# AUTONOMY STATES
# ==============================
class State(Enum):
    IDLE = 0
    REQUEST_DIG = 1
    WAIT_DIG_DONE = 2
    REQUEST_DUMP = 3
    WAIT_DUMP_DONE = 4
    RESET = 5
    COMPLETE = 6
    ERROR = 7

# ==============================
# UART SETUP
# ==============================
try:
    stm = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    time.sleep(2)
    print(f"[OK] Connected to STM32 on {SERIAL_PORT}")
except Exception as e:
    print(f"[FATAL] UART connection failed: {e}")
    exit()

def send(cmd):
    print(f"[JETSON → STM] {cmd}")
    stm.write((cmd + "\n").encode())

def receive():
    if stm.in_waiting:
        msg = stm.readline().decode().strip()
        print(f"[STM → JETSON] {msg}")
        return msg
    return None

# ==============================
# AUTONOMY STATE MACHINE
# ==============================
state = State.IDLE
dig_attempts = 0

try:
    while True:

        if state == State.IDLE:
            print("\n[AUTONOMY] Starting bucket automation (NO CAMERA)")
            dig_attempts = 0
            state = State.REQUEST_DIG

        elif state == State.REQUEST_DIG:
            send("DIG_START")     # Worm gear ON
            state = State.WAIT_DIG_DONE

        elif state == State.WAIT_DIG_DONE:
            msg = receive()
            if msg == "DIG_DONE":
                state = State.REQUEST_DUMP
            elif msg == "ERROR":
                state = State.ERROR

        elif state == State.REQUEST_DUMP:
            send("DUMP")          # Linear actuator / gyro-based dump
            state = State.WAIT_DUMP_DONE

        elif state == State.WAIT_DUMP_DONE:
            msg = receive()
            if msg == "DUMP_DONE":
                state = State.RESET
            elif msg == "ERROR":
                state = State.ERROR

        elif state == State.RESET:
            send("RESET")         # Bucket back to home
            time.sleep(1)
            state = State.COMPLETE

        elif state == State.COMPLETE:
            print("\n✅ [AUTONOMY] Bucket automation completed")
            break

        elif state == State.ERROR:
            print("\n❌ [ERROR] Automation aborted")
            send("ABORT")
            break

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🚨 [EMERGENCY] User interrupt")
    send("ABORT")

finally:
    stm.close()
    print("[INFO] UART closed")
