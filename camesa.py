import cv2

# Replace with your camera's RTSP URL
rtsp_url = 'rtsp://169.254.0.99:554/live.sdp'

# Create a VideoCapture object
cap = cv2.VideoCapture(rtsp_url)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If frame is read correctly, ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Display the resulting frame
    cv2.imshow('IP Camera stream', frame)

    # Press 'q' on keyboard to exit
    if cv2.waitKey(1) == ord('q'):
        break

# When everything done, release the VideoCapture object
cap.release()

# Close all OpenCV windows
cv2.destroyAllWindows()
