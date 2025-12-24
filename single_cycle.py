import time
import sys

try:
    import serial
except Exception:
    serial = None

SERIAL_PORT = "/dev/ttyTHS1"
BAUDRATE = 115200

DIG_TIMEOUT = 10.0
DUMP_TIMEOUT = 10.0
RESET_TIMEOUT = 6.0

stm = None

if serial is not None:
    try:
        stm = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            timeout=0.5
        )
        time.sleep(2)
    except Exception:
        stm = None

def send(cmd):
    try:
        if stm is not None:
            stm.write((cmd + "\n").encode())
        else:
            pass
    except Exception:
        pass

def wait_for(expected, timeout):
    start = time.time()
    while (time.time() - start) < timeout:
        try:
            if stm is not None and stm.in_waiting:
                msg = stm.readline().decode(errors="ignore").strip()
                if msg == expected:
                    return True
                if msg == "ERROR":
                    return False
        except Exception:
            return False
        time.sleep(0.1)
    return False

try:
    send("DIG_START")
    if not wait_for("DIG_DONE", DIG_TIMEOUT):
        raise Exception("DIG_FAILED")

    send("DUMP")
    if not wait_for("DUMP_DONE", DUMP_TIMEOUT):
        raise Exception("DUMP_FAILED")

    send("RESET")
    wait_for("RESET_DONE", RESET_TIMEOUT)

except KeyboardInterrupt:
    send("ABORT")

except Exception:
    send("ABORT")

finally:
    try:
        if stm is not None:
            stm.close()
    except Exception:
        pass
    sys.exit(0)
