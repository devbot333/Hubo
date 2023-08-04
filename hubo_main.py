import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import requests
import json
import base64
import time


#______________________________Reading staff names from the text file

staff_names = {}
text_file_path = "staff_names.txt"
with open(text_file_path, 'r') as file:
    for line in file:
        line = line.strip().split(',')
        #data[name] = ID
        staff_names[line[1]] = line[0]


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
log_filename = f"logs/Detected_Logs_{current_date}.csv"
detected_faces = set()
face_counts = {}
last_published = datetime.now()
unknown_count = 0
unknown_publish_count = 0
api_url = 'https://hubo2.domainenroll.com/api/v1/save-unknown'
API_TOKEN = "ebcc162f5fc3445da79cf5d77c5d6b2d"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cv2.namedWindow("Video Stream")
i = 0 
recognition_count=0
recognized_name = ""
who_dis = 0
check = False

dana_uuid = "02905026-3046-11ee-a913-0242ac120002"
dana_name = "Dana"
fathimat_uuid = "0d8bfe17-304f-11ee-a913-0242ac120002"
fathimat_name = "Fathimat"
harish_uuid = "41d011bb-328d-11ee-a913-0242ac120002"
harish_name = "Harish"
vivek_uuid = "5d79647a-304f-11ee-a913-0242ac120002"
vivek_name = "Vivek"

#______________________________API functions

def add_person(name, image_path, collections = ""):
    if image_path.startswith("https://"):
        files = {"photos": image_path}
    else:
        files = {"photos": open(image_path, "rb")}

    response = requests.post(
        url="https://api.luxand.cloud/v2/person",
        headers={"token": API_TOKEN},
        data={"name": name, "store": "1", "collections": collections},
        files=files,
    )

    if response.status_code == 200:
    	person = response.json()

    	print("Added person", name, "with UUID", person["uuid"])
    	return person["uuid"]
    else:
    	print("Can't add person", name, ":", response.text)
    	return None
    	
def delete_face():
    response = requests.post(
        url="https://api.luxand.cloud/collection/02a76b24-3046-11ee-a913-0242ac120002/person/e1a32bfb-304e-11ee-a913-0242ac120002",
        headers={"token": API_TOKEN}
    )
    	
def add_face(person_uuid, image_path):
    if image_path.startswith("https://"):
        files = {"photo": image_path}
    else:
        files = {"photo": open(image_path, "rb")}


    response = requests.post(
        url="https://api.luxand.cloud/v2/person/%s" % person_uuid,
        headers={"token": API_TOKEN},
        data={"store": "1"},
        files=files
    )
    
    print(response)
    
def recognize_face(image_path):
    url = "https://api.luxand.cloud/photo/search/v2"
    headers = {"token": API_TOKEN}

    #if image_path.startswith("https://"):
    #    files = {"photo": image_path}
    #else:
    #    files = {"photo": open(image_path, "rb")}
    
    ret, image = cv2.imencode(".jpg", frame)
    files = {"photo": ("image.jpg", image.tobytes(), "image/jpeg")}

    response = requests.post(url, headers=headers, files=files)
    result = json.loads(response.text)

    if response.status_code == 200:
        return response.json()
    else:
        print("Can't recognize people:", response.text)
        return None

def update_logs(log_name, log_frame,log_unknowns):
   timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
   with open(log_filename, "a+") as f:
   
      #___Write it in file      
      f.write(f"{timestamp},{log_name}\n")
      
      #___take a screenshot
      pic_name = "Unknown"+str(log_unknowns)
      folder_path = os.path.join("unknowns_pictures",f"{current_date}")
      save_path = os.path.join("unknowns_pictures",f"{current_date}", pic_name+".png")
      if not os.path.exists(folder_path):
         os.makedirs(folder_path)
      cv2.imwrite(save_path, frame)
      
      #___send to API
      
      if log_name == "Unknown":
         # Read the image file as binary data
         with open(save_path, 'rb') as file:
            image_data = file.read()
       
         base64_image = base64.b64encode(image_data).decode('utf-8')
         payload = {'employee_id': None, 'guest_image': base64_image}
         json_payload = json.dumps(payload)
         headers = {'Content-Type': 'application/json'}
         response = requests.post(api_url, data=json_payload, headers=headers)
         print(response)
        
#Add a person
#path_to_image = "/home/jov/Hubo/staff_pictures/Vivek.jpeg"
#collection_name = "staff"
#person_uuid = add_person(person_name, path_to_image, collection_name)
        
#Add face to pre-existing person
#add_face(ritin_uuid, "/home/jov/Hubo/staff_pictures/Ritin/Ritin1.jpeg")


#______________________________Start loop



try:
    while True:
        # Capture frame-by-frame from the camera
        ret, frame = cap.read()

        # If the frame was not captured successfully, exit the loop
        if not ret:
            break
            
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale frame
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if (datetime.now() - last_published) >= timedelta(minutes=0.15):
           if not check:
              #print("its been more than a minute since someone was known")
              pass
           check = True
        
        num_faces = len(faces)
        
        if num_faces>0:
           i+=1
           if i>2 and recognition_count<3:
              recognition_count+=1
              recognized = recognize_face(frame)
              if recognized:
                 recognized_name = recognized[0]["name"]
                 print("Recognized: ", recognized)
                 client.publish(topic, staff_names[recognized[0]["name"]])
                 print("published msg for ",recognized[0]["name"],staff_names[recognized[0]["name"]])
                 update_logs(recognized_name, frame, 3)
                 last_published = datetime.now()
                 check = False
              else:
                 who_dis+=1
                 #if check and who_dis > 3:
                 if who_dis > 3:
                    unknown_count+=1
                    print("Who dis?")
                    recognized_name = "Unknown"
                    client.publish(topic,"Unknown")
                    print("published msg for Unknown")
                    update_logs(recognized_name, frame, unknown_count)
                    who_dis = 0
                 if not check:
                    print("its seeing unknown, but it prbably isnt so will not publish")
                    
              i=0
        else:
           i=0
           recognition_count=0
         

        # Draw rectangles around the detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display the frame in the OpenCV window........
        cv2.imshow("Video Stream", frame)

        # Check for key press to stop the video stream
        if cv2.waitKey(1) == ord('q'):
            break

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()




