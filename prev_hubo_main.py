import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import requests
import json
import base64


#______________________________Reading data from the text file

data = {}
text_file_path = "staff_names.txt"
with open(text_file_path, 'r') as file:
    for line in file:
        line = line.strip().split(',')
        #data[name] = ID
        data[line[1]] = line[0]
        

#______________________________Load images & known names from the "staff" folder

resources_path = "staff_pictures"
known_images = []
known_names = []
for filename in os.listdir(resources_path):
    if filename.endswith(".jpeg"):
        name = os.path.splitext(filename)[0]
        image = face_recognition.load_image_file(os.path.join(resources_path, filename))
        encoding = face_recognition.face_encodings(image)[0]
        known_images.append(encoding)
        known_names.append(name)


#______________________________MQTT 

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to the broker!")
    else:
        print("Failed to connect to the broker!")
        
def on_publish(client, userdata, mid):
    print("Message Successfully Published")

broker = 'sonic.domainenroll.com'
name = 'domainenroll'
passwd = 'de120467'
topic = '/user_data'

client = mqtt.Client()
client.username_pw_set(name, passwd)
client.on_connect = on_connect
client.on_publish = on_publish

client.connect(broker)
client.loop_start()


#______________________________Initialize the video capture

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#______________________________Variables

current_date = datetime.now().date()
log_filename = f"Detected_Logs_{current_date}.csv"
detected_faces = set()
face_counts = {}
unknown_count = 0
unknown_publish_count = 0
last_published = {}
api_url = 'https://hubo2.domainenroll.com/api/v1/save-unknown'

#______________________________ start loop

while True:
    # Read frame from the video capture
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame from BGR (OpenCV default) to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform face detection on the frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        # Compare the face encoding with the known images
        matches = face_recognition.compare_faces(known_images, face_encoding)
        name = "Unknown"

        # Find the best match
        face_distances = face_recognition.face_distance(np.array(known_images), face_encoding)
        min_distance_index = np.argmin(face_distances)
        if matches[min_distance_index] and face_distances[min_distance_index] < 0.5:
            name = known_names[min_distance_index]

        face_names.append(name)



    #Log faces in the same file and publish MQTT messages
    with open(log_filename, "a+") as f:
        for name in face_names:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if name == "Unknown":
            	unknown_publish_count+=1
            	if unknown_publish_count > 10:
            	
            	    #___Update variables
            	    name = "Unknown"+str(unknown_count)
            	    unknown_count+=1
            	    unknown_publish_count = 0
            	             	    
            	    #___Write it in file            	    
            	    detected_faces.add(name)
            	    f.write(f"{timestamp},{name}\n")
            	    
            	    #___publish MQTT
            	    client.publish(topic, "Unknown")
            	    print("Published MQTT message for Unknown")
  
            	    #___take a screenshot
            	    folder_path = os.path.join("unknowns_pictures",f"{current_date}")
            	    save_path = os.path.join("unknowns_pictures",f"{current_date}", name+".png")
            	    
            	    if not os.path.exists(folder_path):
            	    	os.makedirs(folder_path)
            	    	
            	    cv2.imwrite(save_path, frame)
            	    
            	    #___send to API
            	    
            	    # Read the image file as binary data
            	    with open(save_path, 'rb') as file:
            	        image_data = file.read()
                    	
            	    #Convert the image data to base64
            	    base64_image = base64.b64encode(image_data).decode('utf-8')
            	    
            	    # Set request payload as JSON
            	    payload = {'employee_id': None, 'guest_image': base64_image}
            	    
            	    # Convert payload to JSON string
            	    json_payload = json.dumps(payload)
            	    
            	    # Set request headers
            	    headers = {'Content-Type': 'application/json'}
            	    
            	    # Send POST request with JSON payload
            	    response = requests.post(api_url, data=json_payload, headers=headers)
            	    print(response)
                    
            else:
                # Check if enough time has passed since the last published time
                if name not in last_published or (datetime.now() - last_published[name]) >= timedelta(minutes=5):
                
                    if name in data:
                    	#Publish name to MQTT
                        client.publish(topic, data[name])
                        print("Published MQTT message for", name)
                        
                        #Write name in file
                        detected_faces.add(name)
                        f.write(f"{timestamp},{name}\n")

                    # Update the last published time for the detected face
                    last_published[name] = datetime.now()
                    

    # Draw bounding boxes and display names
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Draw the bounding box
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Display the name
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow("Video", frame)

    # Check if the date has changed and update it
    if datetime.now().date() != current_date:
        # Update the current date and log filename
        current_date = datetime.now().date()
        log_filename = f"Detected_Logs_{current_date}.csv"
        detected_faces.clear()
        last_published = datetime.now()

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()

