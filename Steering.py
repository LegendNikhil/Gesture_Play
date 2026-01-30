import cv2
import numpy as np
from pynput.keyboard import Controller

# Initialize the keyboard controller
keyboard = Controller()

# Define a function to send keypress
def send_keypress(action):
    if action:
        keyboard.press(action.lower())
        keyboard.release(action.lower())

# Function to determine movement based on circle position and radius
def determine_action(center, prev_center, radius, prev_radius):
    if not prev_center:
        return None
    
    x, y = center
    prev_x, prev_y = prev_center
    
    # Vertical movement
    if y < prev_y - 10:  # Circle moves up
        return "W"  # Accelerate
    elif y > prev_y + 10:  # Circle moves down
        return "S"  # Reverse

    # Horizontal movement
    if x > prev_x + 10:  # Clockwise rotation (right turn)
        return "D"  # Turn Right
    elif x < prev_x - 10:  # Counterclockwise rotation (left turn)
        return "A"  # Turn Left

    return None

# Initialize variables for tracking
prev_center = None
prev_radius = None

# Open the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocess the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # Detect circles using HoughCircles
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=50,
        param1=50,
        param2=30,
        minRadius=20,
        maxRadius=100
    )

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])  # x, y center of the circle
            radius = i[2]          # Radius of the circle
            
            # Draw the detected circle
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            cv2.circle(frame, center, 2, (0, 0, 255), 3)  # Draw the center

            # Determine the action based on movement
            action = determine_action(center, prev_center, radius, prev_radius)
            if action:
                send_keypress(action)

            # Update previous values
            prev_center = center
            prev_radius = radius
            break  # Only handle the first detected circle

    # Display the video feed
    cv2.imshow("Steering Control", frame)

    # Break on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
