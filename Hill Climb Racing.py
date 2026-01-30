import cv2
import mediapipe as mp
from pynput.keyboard import Controller, Key

# Initialize Mediapipe Hand detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize keyboard controller
keyboard = Controller()

def detect_hand_gesture(hand_landmarks, image_width):
    """
    Detect gestures based on hand landmarks.
    - Open palm of left hand for brake.
    - Open palm of right hand for gas.
    """
    thumb_tip = hand_landmarks[mp_hands.HandLandmark.THUMB_TIP].x * image_width
    index_tip = hand_landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width
    pinky_tip = hand_landmarks[mp_hands.HandLandmark.PINKY_TIP].x * image_width

    # If all fingers are spread (open palm), x-coordinates of landmarks will differ significantly
    return abs(thumb_tip - pinky_tip) > 100 and abs(thumb_tip - index_tip) > 50

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip and convert image to RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame for hand landmarks
    results = hands.process(rgb_frame)

    # Keyboard control flags
    left_hand_active = False
    right_hand_active = False

    if results.multi_hand_landmarks:
        for hand_landmark, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_draw.draw_landmarks(frame, hand_landmark, mp_hands.HAND_CONNECTIONS)

            # Determine if the hand is left or right
            hand_label = hand_info.classification[0].label

            if detect_hand_gesture(hand_landmark.landmark, frame.shape[1]):
                if hand_label == "Left":
                    left_hand_active = True
                elif hand_label == "Right":
                    right_hand_active = True

    # Send keyboard inputs
    if left_hand_active:
        keyboard.press(Key.left)
    else:
        keyboard.release(Key.left)

    if right_hand_active:
        keyboard.press(Key.right)
    else:
        keyboard.release(Key.right)

    # Display the video frame
    cv2.imshow("Gesture Control", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
