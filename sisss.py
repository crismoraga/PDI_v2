import numpy as np
import pyfakewebcam
import time

cam = pyfakewebcam.FakeWebcam('/dev/video10', 640, 480)

frame = np.zeros((480, 640, 3), dtype=np.uint8)
frame[:, :, 0] = 255  # rojo

while True:
    cam.schedule_frame(frame)
    time.sleep(1/30)
