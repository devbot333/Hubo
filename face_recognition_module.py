import cv2
import face_recognition

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cv2.namedWindow("Video Stream")

try:
    while True:
        # Capture frame-by-frame from the camera
        ret, frame = camera.read()

        # If the frame was not captured successfully, exit the loop
        if not ret:
            break
            
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        
        faces = face_recognition.face_locations(gray_frame)
        
        if len(faces)>0:
           print("there is a face")

        # Display the frame in the OpenCV window
        cv2.imshow("Video Stream", frame)

        # Check for key press to stop the video stream
        if cv2.waitKey(1) == ord('q'):
            break

finally:
    # Release resources
    camera.release()
    cv2.destroyAllWindows()
