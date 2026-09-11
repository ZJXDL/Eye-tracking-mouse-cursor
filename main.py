import cv2
import mediapipe as mp
import pyautogui
import math
import time

# ---------------------------
# Config
# ---------------------------
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

CAM_W, CAM_H = 640, 480
SMOOTHING_ALPHA = 0.35       # higher = snappier, lower = smoother
BLINK_THRESHOLD = 0.20       # normalized ratio threshold
BLINK_CONSEC_FRAMES = 3      # blink must persist this many frames
CLICK_COOLDOWN_SEC = 0.6

# Calibration box for gaze remapping
# You should tune or replace this with a real calibration routine later.
GAZE_X_MIN = 0.38
GAZE_X_MAX = 0.62
GAZE_Y_MIN = 0.38
GAZE_Y_MAX = 0.58   # smaller eye-motion vertical range gets stretched to full screen

# ---------------------------
# Helpers
# ---------------------------
def px(landmark, w, h):
    return landmark.x * w, landmark.y * h

def dist2d(a, b, w, h):
    ax, ay = px(a, w, h)
    bx, by = px(b, w, h)
    return math.hypot(ax - bx, ay - by)

def clamp(v, lo, hi):
    return max(lo, min(v, hi))

def remap(value, in_min, in_max, out_min, out_max):
    if abs(in_max - in_min) < 1e-6:
        return out_min
    t = (value - in_min) / (in_max - in_min)
    t = clamp(t, 0.0, 1.0)
    return out_min + t * (out_max - out_min)

def eye_aspect_ratio(landmarks, top_idx, bottom_idx, left_idx, right_idx, w, h):
    vertical = dist2d(landmarks[top_idx], landmarks[bottom_idx], w, h)
    horizontal = dist2d(landmarks[left_idx], landmarks[right_idx], w, h)
    if horizontal == 0:
        return 1.0
    return vertical / horizontal

# ---------------------------
# Init
# ---------------------------
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # may help on some systems

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

screen_w, screen_h = pyautogui.size()

smoothed_x = screen_w / 2
smoothed_y = screen_h / 2

blink_counter = 0
last_click_time = 0

prev_time = time.time()

while True:
    ok, frame = cam.read()
    if not ok:
        continue

    frame = cv2.flip(frame, 1)
    frame_h, frame_w = frame.shape[:2]

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    fps = 1.0 / max(time.time() - prev_time, 1e-6)
    prev_time = time.time()

    if result.multi_face_landmarks:
        landmarks = result.multi_face_landmarks[0].landmark

        # -----------------------------------
        # 1) Gaze point from iris center
        # -----------------------------------
        # right iris landmarks: 474, 475, 476, 477
        iris_indices = [474, 475, 476, 477]
        iris_x = sum(landmarks[i].x for i in iris_indices) / len(iris_indices)
        iris_y = sum(landmarks[i].y for i in iris_indices) / len(iris_indices)

        # Remap calibrated gaze box -> full screen
        target_x = remap(iris_x, GAZE_X_MIN, GAZE_X_MAX, 0, screen_w)
        target_y = remap(iris_y, GAZE_Y_MIN, GAZE_Y_MAX, 0, screen_h)

        # Exponential smoothing (less lag than moving average)
        smoothed_x = SMOOTHING_ALPHA * target_x + (1 - SMOOTHING_ALPHA) * smoothed_x
        smoothed_y = SMOOTHING_ALPHA * target_y + (1 - SMOOTHING_ALPHA) * smoothed_y

        pyautogui.moveTo(int(smoothed_x), int(smoothed_y))

        # -----------------------------------
        # 2) Blink detection using normalized ratio
        # Left eye example
        # top=159, bottom=145, left corner=33, right corner=133
        # -----------------------------------
        ear = eye_aspect_ratio(
            landmarks,
            top_idx=159,
            bottom_idx=145,
            left_idx=33,
            right_idx=133,
            w=frame_w,
            h=frame_h
        )

        current_time = time.time()

        if ear < BLINK_THRESHOLD:
            blink_counter += 1
        else:
            if blink_counter >= BLINK_CONSEC_FRAMES:
                if current_time - last_click_time > CLICK_COOLDOWN_SEC:
                    pyautogui.click()
                    last_click_time = current_time
            blink_counter = 0

        # -----------------------------------
        # Debug visuals
        # -----------------------------------
        for i in iris_indices:
            x = int(landmarks[i].x * frame_w)
            y = int(landmarks[i].y * frame_h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        top_pt = landmarks[159]
        bottom_pt = landmarks[145]
        top_x, top_y = int(top_pt.x * frame_w), int(top_pt.y * frame_h)
        bot_x, bot_y = int(bottom_pt.x * frame_w), int(bottom_pt.y * frame_h)
        cv2.circle(frame, (top_x, top_y), 3, (0, 255, 255), -1)
        cv2.circle(frame, (bot_x, bot_y), 3, (0, 255, 255), -1)

        cv2.putText(frame, f"EAR: {ear:.3f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Eye Controlled Mouse", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()