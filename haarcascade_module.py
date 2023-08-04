import cv2
import os
import requests
import json
import base64


API_TOKEN = "ebcc162f5fc3445da79cf5d77c5d6b2d"


camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cv2.namedWindow("Video Stream")

i=0
try:
    while True:
        # Capture frame-by-frame from the camera
        ret, frame = camera.read()

        # If the frame was not captured successfully, exit the loop
        if not ret:
            break
            
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale frame
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces)>0:
           i+=1
           print("Face detected: ",i)
           if i>2:
              cv2.imwrite("test_img.jpg", frame)
              print("picture taken!")
              i=0
        else:
           i=0

        # Draw rectangles around the detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display the frame in the OpenCV window
        cv2.imshow("Video Stream", frame)

        # Check for key press to stop the video stream
        if cv2.waitKey(1) == ord('q'):
            break

finally:
    # Release resources
    camera.release()
    cv2.destroyAllWindows()

