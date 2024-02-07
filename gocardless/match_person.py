import numpy as np
import cv2
import face_recognition
import csv
import pandas as pd
from datetime import datetime

# Load data from known_faces.xlsx file
def match_person():
    
    df_known_faces = pd.read_excel('known_faces.xlsx')
    # -------- Extract face encodings and names from the DataFrame ----------
    known_face_encodings = [np.fromstring(encoding.strip('[]'), dtype=float, sep=' ') 
                            for encoding in df_known_faces['Face Encoding']]
    known_face_names = df_known_faces['Face Name'].tolist()
    users = known_face_names.copy()
    print("Users : ",users)
    video_capture = cv2.VideoCapture(0)
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    csv_file_name = current_date + '_matches.csv'
    with open(csv_file_name, 'w', newline='') as f:
        line_writer = csv.writer(f)

        while True:
            # --------- Capture frame-by-frame ---------
            ret, frame = video_capture.read()

            if not ret:
                print("Error: Could not capture frame.")
                break

            # -------- Resize frame for faster processing --------
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

            # -------- Find face locations ----------
            face_locations = face_recognition.face_locations(rgb_small_frame)

            # -------- Find face encodings ---------
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            # -------- Recognize faces if face locations are found -------
            if len(face_locations) > 0:
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = ""

                    if True in matches:
                        first_match_index = matches.index(True)
                        name = known_face_names[first_match_index]
                        print("Name: ", name)

                        # ------ Remove recognized user --------
                        if name in users:
                            print('User removed:', name)
                            users.remove(name)
                            current_time = now.strftime("%H-%M-%S")
                            line_writer.writerow([name, current_time])

            # ------ Display the resulting frame --------
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Release the capture
    video_capture.release()
    cv2.destroyAllWindows()

    print("Recognition ended. Users recorded:", users)
    
# ----- calling function ------
match_person()
