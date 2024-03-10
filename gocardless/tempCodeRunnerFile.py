
import numpy as np
import cv2
import face_recognition
import csv
import os
from datetime import datetime

print('----- Face-Fair ------')
# ------------ Opening the camera-------------
video_capture = cv2.VideoCapture(0)

# Directory containing the images of known faces
images_directory = "assets"
known_face_encodings = []
known_face_names = []

# ------------ Loading Images --------------
for filename in os.listdir(images_directory):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(images_directory, filename)
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if len(face_encodings) > 0:
            known_face_encodings.append(face_encodings[0])
            known_face_names.append(os.path.splitext(filename)[0])
        else:
            print("No face found in", image_path)

print("Known face names:", known_face_names)
users = known_face_names.copy()
print("Users : ",users)

# Open CSV file for writing
now = datetime.now()
current_date = now.strftime("%Y-%m-%d")
csv_file_name = current_date + '.csv'
# -------------- Camera On -----------------------
with open(csv_file_name, 'w', newline='') as f:
    line_writer = csv.writer(f)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        if not ret:
            print("Error: Could not capture frame.")
            break

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        # Find face locations
        face_locations = face_recognition.face_locations(rgb_small_frame)
        # print("Face Location is : ",face_locations)

        # Find face encodings
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        # print("FACE LOCATIONS ")

        # Recognize faces if face locations are found
        if len(face_locations) > 0:
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                # print("Matches  : ", matches)
                name = ""

                if True in matches:
                    # print("yay")
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    print("name  : ",name)

                    # Remove recognized user
                    if name in users:
                        print('user removed', name)
                        users.remove(name)
                        current_time = now.strftime("%H-%M-%S")
                        line_writer.writerow([name, current_time])
                    else:
                        print("User not present")

        # Display the resulting frame
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the capture
video_capture.release()
cv2.destroyAllWindows()

print("Recognition ended. Users recorded:", users)
