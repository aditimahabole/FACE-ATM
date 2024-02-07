import pandas as pd
import face_recognition
import os

def save_photos_encodings():
    print('----- Face Fair Save Encodings ------')
    images_directory = "assets"
    known_face_encodings = []
    known_face_names = []

    # Check if the Excel file already exists
    excel_file_name = 'known_faces.xlsx'
    if os.path.exists(excel_file_name):
        # Load existing data from Excel
        df_existing = pd.read_excel(excel_file_name)
        known_face_encodings = df_existing['Face Encoding'].tolist()
        known_face_names = df_existing['Face Name'].tolist()

    # Saving new photos encodings 
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
    print("Users : ", users)

    # Create a DataFrame with the new data
    df_new = pd.DataFrame(data={'Face Name': known_face_names, 'Face Encoding': known_face_encodings})

    # Append new data to the existing DataFrame (if it exists)
    if os.path.exists(excel_file_name):
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    # Save the combined DataFrame to Excel
    df_combined.to_excel(excel_file_name, index=False)
    print(f"Face encodings appended to '{excel_file_name}'")

# ---------Calling the function --------------
save_photos_encodings()
