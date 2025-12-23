#values to be adjusted: 
# x1 = 0.30 * w   # left
# x2 = 0.70 * w   # right
# y1 = 0.50 * h   # top
# y2 = 0.80 * h   # bottom
# Rule of thumb:

# Horizontal: bucket width-oda middle 40–50%

# Vertical: bucket depth-oda bottom half

# Green box bucket ulla full-aa irukkanum

import depthai as dai
import cv2
import numpy as np

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

while True:
    depthFrame = q.get().getFrame()

    depth_vis = cv2.normalize(depthFrame, None, 0, 255, cv2.NORM_MINMAX)
    depth_vis = depth_vis.astype(np.uint8)
    depth_vis = cv2.cvtColor(depth_vis, cv2.COLOR_GRAY2BGR)

    h, w = depthFrame.shape

    #INITIAL ROI (we will tune this)
    x1, y1 = int(0.35*w), int(0.45*h)
    x2, y2 = int(0.65*w), int(0.75*h)

    cv2.rectangle(depth_vis, (x1,y1), (x2,y2), (0,255,0), 2)

    cv2.imshow("ROI Tuning", depth_vis)
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
device.close()
