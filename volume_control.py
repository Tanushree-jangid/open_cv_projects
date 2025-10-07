import cv2
import time
import math
import numpy as np
import HandTrackingModule as htm  # Make sure you have this module

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- Camera settings ---
wCam, hCam = 640, 480

# --- Initialize camera ---
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0

# --- Initialize hand detector ---
detector = htm.handDetector(detectionCon=0.7)

# --- Initialize system volume ---
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame")
        break

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if lmList:
        # Thumb tip = 4, Index tip = 8
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]

        # Center between thumb and index
        cx, cy = (x1 + x2)//2, (y1 + y2)//2

        # Draw circles and line
        cv2.circle(img, (x1, y1), 10, (255,0,0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255,0,0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (0,255,0), 3)
        cv2.circle(img, (cx, cy), 10, (0,0,255), cv2.FILLED)

        # Length between fingers
        length = math.hypot(x2 - x1, y2 - y1)

        # Convert hand range (50-300) to volume range
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volume.SetMasterVolumeLevel(vol, None)

        # Optional: change color if fingers are very close
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0,255,0), cv2.FILLED)

        # Draw volume bar
        cv2.rectangle(img, (50, 150), (85, 400), (0,255,0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0,255,0), cv2.FILLED)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 3)

    cv2.imshow("Hand Volume Control", img)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
