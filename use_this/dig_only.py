import time
import sys

try:
    import serial
except Exception:
    serial = None

SERIAL_PORT = "/dev/ttyTHS1"
BAUDRATE = 115200

HOME_ANGLE = -45.0
DIG_ANGLE = -28.0
MAX_SAFE_ANGLE = 35.0

DIG_TIMEOUT = 8.0
ANGLE_JUMP_LIMIT = 10.0

esp = None
if serial is not None:
    try:
        esp = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
        time.sleep(2)
    except Exception:
        esp = None

def motor_forward():
    pass

def motor_stop():
    pass

def get_angle():
    if not esp:
        return None
    try:
        if esp.in_waiting:
            line = esp.readline().decode(errors="ignore").strip()
            if line.startswith("ANGLE:"):
                return float(line.split(":")[1])
    except Exception:
        return None
    return None

last_angle = None

try:
    start_time = time.time()
    motor_forward()

    while True:
        angle = get_angle()

        if angle is not None:
            if last_angle is not None:
                if abs(angle - last_angle) > ANGLE_JUMP_LIMIT:
                    raise Exception("ANGLE_JUMP")
            last_angle = angle

            if angle >= DIG_ANGLE:
                break

            if angle > MAX_SAFE_ANGLE:
                raise Exception("ANGLE_LIMIT")

        if time.time() - start_time > DIG_TIMEOUT:
            raise Exception("DIG_TIMEOUT")

        time.sleep(0.05)

    motor_stop()

except KeyboardInterrupt:
    motor_stop()

except Exception:
    motor_stop()

finally:
    try:
        if esp:
            esp.close()
    except Exception:
        pass
    sys.exit(0)
