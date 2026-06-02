import cv2

# Initialize webcam (0 is usually the default built-in camera)
cap = cv2.VideoCapture(0)

print("Press 'q' to exit the video stream.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame. If your camera is broken, this is expected.")
        break

    # Display the live video feed
    cv2.imshow('Webcam Test', frame)

    # Break loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()