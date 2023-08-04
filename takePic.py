import os
import cv2

def take_picture():
    # Create a video capture object for the default camera (0)
    cap = cv2.VideoCapture(0)

    try:
        # Check if the camera is opened successfully
        if not cap.isOpened():
            raise Exception("Failed to open the camera.")

        count = 1
        folder_path = "/home/jov/Hubo/staff_pictures"
        os.makedirs(folder_path, exist_ok=True)  # Create the folder if it doesn't exist

        while True:
            # Read a frame from the camera
            ret, frame = cap.read()

            # If the frame was not captured successfully, exit the loop
            if not ret:
                break

            # Display the frame in the OpenCV window
            cv2.imshow("Video Stream", frame)

            # Check for key press
            key = cv2.waitKey(1)

            # Save the frame as an image file when the spacebar is pressed
            if key == 32:  # Spacebar key
                image_filename = os.path.join(folder_path, f"pic{count}.jpg")
                cv2.imwrite(image_filename, frame)
                print("Image captured and saved as:", image_filename)
                count += 1

            # Check for key press to stop the video stream
            if key == ord('q'):
                break

    finally:
        # Release resources and close the camera
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    take_picture()

