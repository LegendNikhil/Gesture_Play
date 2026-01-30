import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk
from pynput.keyboard import Controller

# Initialize MediaPipe and keyboard controller
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
keyboard = Controller()

# Gesture Detection Function
def detect_gesture(landmarks):
    if all([landmarks[i].y < landmarks[i - 3].y for i in range(8, 21, 4)]):  # Open palm
        return "W"  # Move Forward
    elif all([landmarks[i].y > landmarks[0].y for i in range(8, 21, 4)]):  # Closed fist
        return "S"  # Move Backward
    elif landmarks[4].x < landmarks[3].x:  # Thumb pointing left
        return "A"  # Turn Left
    elif landmarks[4].x > landmarks[3].x:  # Thumb pointing right
        return "D"  # Turn Right
    else:
        return None

# Send Keypress
def send_keypress(action):
    if action:
        keyboard.press(action.lower())
        keyboard.release(action.lower())

# Update GUI
def update_gui(action, frame):
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    action_label.config(text=f"Detected Action: {action}" if action else "No Action Detected")

# Main Loop for Gesture Detection and GUI
def main_loop():
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    action = None
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            action = detect_gesture(hand_landmarks.landmark)
            send_keypress(action)

    update_gui(action, rgb_frame)
    root.after(10, main_loop)

# Initialize Webcam and Tkinter GUI
cap = cv2.VideoCapture(0)
root = tk.Tk()
root.title("Gesture Control for Car Game")

video_label = tk.Label(root)
video_label.pack()

action_label = tk.Label(root, text="No Action Detected", font=("Arial", 14))
action_label.pack()

# Start the main loop
main_loop()

root.mainloop()
cap.release()
cv2.destroyAllWindows()
