import cv2
import mediapipe as mp
import pyautogui  

# Initialize Mediapipe hands and drawing utils
capture_hands = mp.solutions.hands.Hands()
drawing_option = mp.solutions.drawing_utils
screen_width , screen_height = pyautogui.size()

# Start video capture
camera = cv2.VideoCapture(0)

x1, y1, x2, y2 = 0, 0, 0, 0
clicked = False

while True:
    success, image = camera.read()
    if not success:
        break
    image_height, image_width, _ = image.shape
    image = cv2.flip(image, 1)  # mirror image
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image for hand landmarks
    output_hands = capture_hands.process(rgb_image)
    all_hands = output_hands.multi_hand_landmarks

    # Draw hand landmarks if detected
    if all_hands:
        for hand in all_hands:
            drawing_option.draw_landmarks(image, hand, mp.solutions.hands.HAND_CONNECTIONS)
            one_hand_landmarks = hand.landmark
            for id, lm in enumerate(one_hand_landmarks):
                x = int(lm.x * image_width)
                y = int(lm.y * image_height)
                if id == 8:
                    mouse_x = int(screen_width / image_width * x)
                    mouse_y = int(screen_height / image_height * y)
                    cv2.circle(image,(x,y), 10, (0,255,255))
                    pyautogui.moveTo(mouse_x, mouse_y, duration=0.1)
                    x1, y1 = x, y
                if id == 4:
                    x2, y2 = x, y
                    cv2.circle(image,(x,y), 10, (0,255,255))
        dist = y2 - y1     
        if dist < 20 and not clicked:
            pyautogui.click()
            clicked = True
            print("Clicked")
        elif dist >= 20:
            clicked = False

    # Display the video frame
    cv2.imshow("Hand movement video capture", image)

    # Wait for ESC key to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

camera.release()
cv2.destroyAllWindows()
