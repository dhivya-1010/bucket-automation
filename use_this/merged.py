import time
import sys

# ---------------- SAFE IMPORTS ----------------
try:
    import serial
except Exception:
    serial = None

try:
    import depthai as dai
    import cv2
    import numpy as np
except Exception:
    dai = None
    cv2 = None
    np = None

# ---------------- CONFIG ----------------
SERIAL_PORT = "/dev/ttyTHS1"
BAUDRATE = 115200

HOME_ANGLE = 0.0
DUMP_ANGLE = 55.0
MAX_SAFE_ANGLE = 70.0

DIG_TIME = 3.0
DUMP_TIMEOUT = 8.0
RESET_TIMEOUT = 6.0

TOTAL_CYCLES = 5

DEPTH_VARIANCE_THRESHOLD = 20

# ---------------- UART SETUP ----------------
esp = None
if serial:
    try:
        esp = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
        time.sleep(2)
    except Exception:
        esp = None

# ---------------- MOTOR CONTROL (STUBS) ----------------
def motor_forward():
    pass

def motor_reverse():
    pass

def motor_stop():
    pass

# ---------------- READ ANGLE FROM ESP32 ----------------
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

# ---------------- CAMERA SETUP ----------------
device = None
q = None

if dai:
    try:
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
        q = device.getOutputQueue("depth", maxSize=1, blocking=False)
    except Exception:
        device = None
        q = None

# ---------------- ROI SAND CHECK ----------------
def sand_present():
    if not q or not np:
        return True
    try:
        frame = q.get().getFrame()
        h, w = frame.shape
        x1, x2 = int(0.35*w), int(0.65*w)
        y1, y2 = int(0.45*h), int(0.75*h)
        roi = frame[y1:y2, x1:x2]
        roi = roi[roi > 0]
        if roi.size < 50:
            return False
        return (roi.max() - roi.min()) > DEPTH_VARIANCE_THRESHOLD
    except Exception:
        return False

# ---------------- MAIN AUTOMATION ----------------
try:
    for cycle in range(1, TOTAL_CYCLES + 1):

        motor_forward()
        time.sleep(DIG_TIME)
        motor_stop()

        if not sand_present():
            continue

        start = time.time()
        motor_forward()
        while True:
            angle = get_angle()
            if angle is not None:
                if angle >= DUMP_ANGLE:
                    break
                if angle > MAX_SAFE_ANGLE:
                    raise Exception("ANGLE_LIMIT")
            if time.time() - start > DUMP_TIMEOUT:
                raise Exception("DUMP_TIMEOUT")
            time.sleep(0.05)
        motor_stop()

        start = time.time()
        motor_reverse()
        while True:
            angle = get_angle()
            if angle is not None and angle <= HOME_ANGLE:
                break
            if time.time() - start > RESET_TIMEOUT:
                raise Exception("RESET_TIMEOUT")
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
    try:
        if device:
            device.close()
    except Exception:
        pass
    sys.exit(0)
