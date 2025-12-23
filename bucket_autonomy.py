import serial
import time
from enum import Enum
import depthai as dai
import numpy as np

# ==============================
# CONFIGURATION
# ==============================
SERIAL_PORT = "/dev/ttyTHS1"
BAUDRATE = 115200
MAX_DIG_RETRIES = 2
DEPTH_VARIANCE_THRESHOLD = 20  # mm (tune this)

# ==============================
# AUTONOMY STATES
# ==============================
class State(Enum):
    IDLE = 0
    REQUEST_DIG = 1
    WAIT_DIG_DONE = 2
    CHECK_SAND = 3
    REQUEST_DUMP = 4
    WAIT_DUMP_DONE = 5
    VERIFY_EMPTY = 6
    RESET = 7
    COMPLETE = 8
    ERROR = 9

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
# OAK-D LITE DEPTH SETUP
# ==============================
pipeline = dai.Pipeline()

monoL = pipeline.create(dai.node.MonoCamera)
monoR = pipeline.create(dai.node.MonoCamera)
monoL.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoR.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoL.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoR.setBoardSocket(dai.CameraBoardSocket.RIGHT)

stereo = pipeline.create(dai.node.StereoDepth)
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
monoL.out.link(stereo.left)
monoR.out.link(stereo.right)

xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("depth")
stereo.depth.link(xout.input)

device = dai.Device(pipeline)
depthQueue = device.getOutputQueue("depth", maxSize=1, blocking=False)

# ==============================
# VISION FUNCTIONS
# ==============================
def sand_present():
    inDepth = depthQueue.get()
    depthFrame = inDepth.getFrame()

    h, w = depthFrame.shape

    # ROI INSIDE BUCKET (TUNE THIS)
    x1, y1 = int(0.35 * w), int(0.45 * h)
    x2, y2 = int(0.65 * w), int(0.75 * h)

    roi = depthFrame[y1:y2, x1:x2]
    roi = roi[roi > 0]

    if len(roi) < 50:
        print("[VISION] Not enough depth data")
        return False

    depth_variation = np.max(roi) - np.min(roi)
    print(f"[VISION] Depth variation: {depth_variation} mm")

    return depth_variation > DEPTH_VARIANCE_THRESHOLD

def bucket_empty():
    return not sand_present()

# ==============================
# AUTONOMY STATE MACHINE
# ==============================
state = State.IDLE
dig_attempts = 0

try:
    while True:

        if state == State.IDLE:
            print("\n[AUTONOMY] Starting bucket automation")
            dig_attempts = 0
            state = State.REQUEST_DIG

        elif state == State.REQUEST_DIG:
            send("DIG_START")
            state = State.WAIT_DIG_DONE

        elif state == State.WAIT_DIG_DONE:
            msg = receive()
            if msg == "DIG_DONE":
                state = State.CHECK_SAND
            elif msg == "ERROR":
                state = State.ERROR

        elif state == State.CHECK_SAND:
            if sand_present():
                print("[AUTONOMY] Sand detected")
                state = State.REQUEST_DUMP
            else:
                dig_attempts += 1
                print(f"[WARN] No sand detected. Retry {dig_attempts}")
                if dig_attempts <= MAX_DIG_RETRIES:
                    state = State.REQUEST_DIG
                else:
                    state = State.ERROR

        elif state == State.REQUEST_DUMP:
            send("DUMP")
            state = State.WAIT_DUMP_DONE

        elif state == State.WAIT_DUMP_DONE:
            msg = receive()
            if msg == "DUMP_DONE":
                state = State.VERIFY_EMPTY
            elif msg == "ERROR":
                state = State.ERROR

        elif state == State.VERIFY_EMPTY:
            if bucket_empty():
                print("[AUTONOMY] Bucket empty confirmed")
                state = State.RESET
            else:
                print("[WARN] Bucket not empty → re-dump")
                state = State.REQUEST_DUMP

        elif state == State.RESET:
            send("RESET")
            time.sleep(1)
            state = State.COMPLETE

        elif state == State.COMPLETE:
            print("\n✅ [AUTONOMY] Bucket cycle completed successfully")
            break

        elif state == State.ERROR:
            print("\n❌ [ERROR] Autonomy aborted")
            send("ABORT")
            break

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🚨 [EMERGENCY] User interrupt")
    send("ABORT")

finally:
    stm.close()
    device.close()
    print("[INFO] UART & OAK-D closed")
