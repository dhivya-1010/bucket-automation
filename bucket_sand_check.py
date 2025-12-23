import depthai as dai
import numpy as np
import cv2

# ----------------------------
# DEPTHAI PIPELINE
# ----------------------------
pipeline = dai.Pipeline()

cam = pipeline.create(dai.node.ColorCamera)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
cam.setBoardSocket(dai.CameraBoardSocket.RGB)

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

# ----------------------------
# START DEVICE
# ----------------------------
device = dai.Device(pipeline)
depthQueue = device.getOutputQueue("depth", maxSize=1, blocking=False)

def sand_present():
    """
    Returns True if sand is detected in bucket
    """
    inDepth = depthQueue.get()
    depthFrame = inDepth.getFrame()  # uint16 depth (mm)

    # ---- ROI: adjust this for your bucket ----
    h, w = depthFrame.shape
    x1, y1 = int(0.35*w), int(0.45*h)
    x2, y2 = int(0.65*w), int(0.75*h)

    roi = depthFrame[y1:y2, x1:x2]

    # Remove zero-depth pixels
    roi = roi[roi > 0]
    if len(roi) < 50:
        return False

    depth_variation = np.max(roi) - np.min(roi)

    print(f"[VISION] Depth variation: {depth_variation} mm")

    # ---- Threshold (tune this) ----
    return depth_variation > 20   # 20–30mm works well
