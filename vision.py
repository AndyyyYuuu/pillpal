from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2
import mediapipe as mp
mp_pose = solutions.pose
pose = mp_pose.Pose(
    model_complexity=1,
)

SCALE_FACTOR = 0.1
camera = cv2.VideoCapture(0)
width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
TARGET_WIDTH = int(width * SCALE_FACTOR)
TARGET_HEIGHT = int(height * SCALE_FACTOR)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, TARGET_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, TARGET_HEIGHT)
camera.set(cv2.CAP_PROP_FPS, 15)

def get_landmarks(frame: np.ndarray):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return pose.process(rgb_frame)
    
def draw_specific_landmarks(frame, landmarks, landmark_indices, scale_x, scale_y):
    if landmarks:
        for idx in landmark_indices:
            if idx < len(landmarks):
                landmark = landmarks[idx]
                
                # Convert normalized coords to small frame, then scale up
                x = int(landmark.x * scale_x)
                y = int(landmark.y * scale_y)
                
                cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)  # Larger circles
                cv2.putText(frame, str(idx), (x + 15, y - 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)
    
    return frame

def dist(landmark1, landmark2):
    return np.sqrt((landmark1.x - landmark2.x)**2 + (landmark1.y - landmark2.y)**2)


def vision(display=False):
    
    ret, frame = camera.read()
    original_height, original_width = frame.shape[:2]

    small_frame = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT))
    y = get_landmarks(small_frame)
    if y.pose_landmarks:
        landmarks = y.pose_landmarks.landmark
        if display:
            small_frame = draw_specific_landmarks(small_frame, landmarks, [9, 10, 19, 20], TARGET_WIDTH, TARGET_HEIGHT)
            cv2.imshow("frame", small_frame)
        THRESHOLD = 0.1
        if dist(landmarks[9], landmarks[19]) < THRESHOLD\
        or dist(landmarks[10], landmarks[20]) < THRESHOLD:
            return True
        else:
            return False

    if display:
        cv2.imshow("frame", small_frame)
    return False

'''
camera.release()
cv2.destroyAllWindows()


while True:
    print(vision())
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
'''