from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True)
detector = vision.PoseLandmarker.create_from_options(options)
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
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    return detector.detect(mp_image)

# TODO: Debug this function (issue arises after scaling)
def draw_specific_landmarks(frame, landmarks, landmark_indices, scale_x, scale_y):
    """Draw specific landmarks on the frame"""
    if landmarks and len(landmarks) > 0:
        pose_landmarks = landmarks[0]
        height, width = frame.shape[:2]
        
        for idx in landmark_indices:
            if idx < len(pose_landmarks):
                landmark = pose_landmarks[idx]
                # Convert normalized coordinates to pixel coordinates
                x = int(landmark.x * width * scale_x)
                y = int(landmark.y * height * scale_y)
                
                # Draw circle for the landmark
                cv2.circle(frame, (x, y), 8, (255, 0, 0), -1)
                
                # Draw landmark number
                cv2.putText(frame, str(idx), (x + 10, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    return frame

def dist(landmark1, landmark2):
    return np.sqrt((landmark1.x - landmark2.x)**2 + (landmark1.y - landmark2.y)**2)

def vision(display=False):
    ret, frame = camera.read()
    original_height, original_width = frame.shape[:2]

    small_frame = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT))
    y = get_landmarks(small_frame)
    if len(y.pose_landmarks) > 0:
        
        scale_x = original_width / TARGET_WIDTH
        scale_y = original_height / TARGET_HEIGHT
        if display:
            small_frame = draw_specific_landmarks(small_frame, y.pose_landmarks, [9, 10, 19, 20], scale_x, scale_y)
            cv2.imshow("frame", small_frame)
        THRESHOLD = 0.1
        if dist(y.pose_landmarks[0][9], y.pose_landmarks[0][19]) < THRESHOLD\
        or dist(y.pose_landmarks[0][10], y.pose_landmarks[0][20]) < THRESHOLD:
            return True
        else:
            return False
    if display:
        cv2.imshow("frame", small_frame)
    return False

'''
while True:
    print(vision())
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()
'''

