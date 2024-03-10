from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Person , BankDetails
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.core.files.storage import FileSystemStorage
# ------------Image recognition ---------------
import numpy as np
import cv2
import face_recognition
import csv
import pandas as pd
from datetime import datetime
import pandas as pd
import face_recognition
import os
from PIL import Image
import io
from django.http import JsonResponse
# -------------OTP-----------------
import random
import smtplib
from email.mime.text import MIMEText
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
# --------------------OTP PART------------------------------
def generate_otp():
    # Generate 4-digit OTP
    otp = random.randint(1000, 9999)
    return str(otp)
    
def send_email_otp(email, otp):
    # Email configuration
    smtp_server = 'your_smtp_server'
    smtp_port = 587  # Update with your SMTP port
    email_sender = 'your_email@example.com'
    email_password = 'your_email_password'

    try:
        # Validate email
        validate_email(email)
    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Invalid email'})

    # Email content
    message = MIMEText(f'Your OTP is: {otp}')
    message['Subject'] = 'Your OTP'
    message['From'] = email_sender
    message['To'] = email

    # Connect to SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(email_sender, email_password)

    # Send email
    server.sendmail(email_sender, [email], message.as_string())

    # Close connection
    server.quit()

    return JsonResponse({'status': 'success', 'message': 'OTP sent to email'})

def send_sms_otp(phone_number, otp):
    from twilio.rest import Client

    account_sid = 'AC42e3a4420f46028429657594ba1be6f2'
    auth_token = 'd62635753310687fee21d47da70e468e'
    twilio_number = '8586810062'

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=f'Your OTP is: {otp}',
            from_=twilio_number,
            to=phone_number
        )
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'success', 'message': 'OTP sent to phone number'})

# ---------------------IMAGE PART---------------------------
def save_photos_encodings(image_path):
    print('----- Face Fair Save Encodings ------')

    # Load existing data if any
    known_faces_file = 'known_faces.xlsx'
    known_face_encodings = []
    known_face_names = []

    if os.path.exists(known_faces_file):
        df_known_faces = pd.read_excel(known_faces_file)
        known_face_encodings = df_known_faces['Face Encoding'].tolist()
        known_face_names = df_known_faces['Face Name'].tolist()

    # Load image and encode faces
    full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
    print("file path is : ", full_image_path)  # Construct full path to the image
    image = face_recognition.load_image_file(full_image_path)
    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) > 0:
        # Check if the face encoding already exists
        new_encoding = face_encodings[0]
        if new_encoding not in known_face_encodings:
            known_face_encodings.append(new_encoding)
            known_face_names.append(os.path.splitext(os.path.basename(image_path))[0])
            print(f"Face encoding added for {known_face_names[-1]}")
        else:
            print("Face encoding already exists for", known_face_names[-1])
    else:
        print("No face found in", image_path)

    # Save updated data
    df_new_faces = pd.DataFrame(data={'Face Name': known_face_names, 'Face Encoding': known_face_encodings})
    if os.path.exists(known_faces_file):
        df_combined = pd.concat([df_known_faces, df_new_faces], ignore_index=True)
    else:
        df_combined = df_new_faces

    df_combined.to_excel(known_faces_file, index=False)
    print(f"Face encodings saved to '{known_faces_file}'")


def match_person(request):
    print("inside match person")
    df_known_faces = pd.read_excel('known_faces.xlsx')
    # -------- Extract face encodings and names from the DataFrame ----------
    known_face_encodings = [np.fromstring(encoding.strip('[]'), dtype=float, sep=' ') 
                            for encoding in df_known_faces['Face Encoding']]
    known_face_names = df_known_faces['Face Name'].tolist()
    users = known_face_names.copy()
    print("Users : ",users)
    print("inside match person 1")
    video_capture = cv2.VideoCapture(0)
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    csv_file_name = current_date + '_matches.csv'
    print("inside match person 2")
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
                            user_detail = users.remove(name)
                            current_time = now.strftime("%H-%M-%S")
                            line_writer.writerow([name, current_time])
                            print("User is removed lets end")
                            print(user_detail)
                            break
                          
                            
                            # End the camera
                            

            # ------ Display the resulting frame --------
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
                break

        # Release the capture
        video_capture.release()
        cv2.destroyAllWindows()

    print("Recognition ended. Users recorded:", users)
    return JsonResponse({'status': 'Recognition started.'})

# --------------------REGISTER PAGE-----------------------------


# def register_page(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         contact = request.POST.get('contact')
#         age = request.POST.get('age')
#         password = request.POST.get('password')
#         image = request.FILES.get('image')
#         bank_name = request.POST.get('bank_name')
#         account_number = request.POST.get('account_number')
#         if Person.objects.filter(username=username).exists():
#             messages.error(request, 'Username already exists!')
#             return redirect('register_page')
#         if Person.objects.filter(email=email).exists():
#             messages.error(request, 'Email already exists!')
#             return redirect('register_page')
#         hashed_password = make_password(password)

#         # Create the user instance
#         user = Person.objects.create(
#             username=username,
#             first_name=first_name,
#             last_name=last_name,
#             email=email,
#             password=hashed_password,
#             contact=contact,
#             age=age
#         )


#         # Save the uploaded image
#         if image:
#             print("image is : ",image)
#             fs = FileSystemStorage(location=settings.MEDIA_ROOT)
#             print("fs is : ",fs)
#             print("file name is : ",image.name)
#             filename = fs.save(image.name, image)
#             user.image = fs.url(filename)

#         # Save bank details
#         bank_details = BankDetails.objects.create(
#             user=user,
#             bank_name=bank_name,
#             account_number=account_number,
           
#         )

#         # Save the user and bank details
#         user.save()
#         bank_details.save()
#         print("User Created : ",user)
#         print("Bank Details : ",bank_details)

#         messages.success(request, 'Account created successfully!')
#         return redirect('login_page')

#     return render(request, 'register.html')


# def register_page(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         contact = request.POST.get('contact')
#         age = request.POST.get('age')
#         password = request.POST.get('password')
#         image = request.FILES.get('image')
#         bank_name = request.POST.get('bank_name')
#         account_number = request.POST.get('account_number')

#         # Check if username or email already exists
#         if Person.objects.filter(username=username).exists():
#             messages.error(request, 'Username already exists!')
#             return redirect('register_page')
#         if Person.objects.filter(email=email).exists():
#             messages.error(request, 'Email already exists!')
#             return redirect('register_page')

#         # Hash the password
#         hashed_password = make_password(password)

#         # Create the user instance
#         user = Person.objects.create(
#             username=username,
#             first_name=first_name,
#             last_name=last_name,
#             email=email,
#             password=hashed_password,
#             contact=contact,
#             age=age
#         )

#         # Rename and save the uploaded image
#         if image:
#             print("saving image")
#             fs = FileSystemStorage(location=settings.MEDIA_ROOT)
#             filename = f"{email}_{contact}_{first_name}.{image.name.split('.')[-1]}"
#             print("filename : ",filename)
#             fs.save(filename, image)
#             user.image = fs.url(filename)
#             print("user image : ", user.image)

#         # Save bank details
#         bank_details = BankDetails.objects.create(
#             user=user,
#             bank_name=bank_name,
#             account_number=account_number,
#         )

#         # Save the user and bank details
#         user.save()
#         bank_details.save()

#         messages.success(request, 'Account created successfully!')
#         return redirect('login_page')

#     return render(request, 'register.html')



def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        age = request.POST.get('age')
        password = request.POST.get('password')
        image = request.FILES.get('image')
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')

        # Check if username or email already exists
        if Person.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register_page')
        if Person.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('register_page')

        # Hash the password
        hashed_password = make_password(password)

        # Create the user instance
        user = Person.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
            contact=contact,
            age=age
        )

        # Rename and save the uploaded image in PNG format
        if image:
            print("saving image")
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = f"{email}_{contact}_{first_name}.png"  # Save as PNG format
            print("filename : ", filename)

            # Open the uploaded image using Pillow
            img = Image.open(image)

            # Create an in-memory stream to save the image
            image_stream = io.BytesIO()
            img.save(image_stream, format='PNG')  # Convert and save as PNG

            # Save the image to the file system
            fs.save(filename, image_stream)
            user.image = fs.url(filename)
            print("user image : ", user.image)
            print("save encodings is called bro")
            image_path = str(filename)
            print(image_path)
            save_photos_encodings(filename)
            print("save encodings ENDS")

        # Save bank details
        bank_details = BankDetails.objects.create(
            user=user,
            bank_name=bank_name,
            account_number=account_number,
        )

        # Save the user and bank details
        user.save()
        bank_details.save()

        messages.success(request, 'Account created successfully!')
        return redirect('login_page')

    return render(request, 'register.html')
# --------------------LOGIN PAGE-----------------------------
from django.contrib.auth import authenticate

def login_page(request):
    print("INSIDE LOGIN")
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = Person.objects.filter(email=email).first()
        print("User login : ",user)
        print("email login : ",email)
        print("password login : ",password)
        if user and check_password(password, user.password):
            user1 = authenticate(request, username=user.username, password=password)
            # print("user1 : ",user1)
            # login(request, user)
            # print(login(request,user))
            request.session['user_email'] = email
            print("YAYAYAYAYAAYAY")
            # Redirect to the home page
            return redirect('home_page')
        else:
            # Handle invalid credentials
            messages.error(request, 'Invalid email or password.')
            return redirect('login_page')

    return render(request, 'login.html')




# def login_page(request):
    
    if request.method == 'POST':
        print('inside if')
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = Person.objects.filter(email=email).first()
        print('email : ',email)
        print('age : ',user.age)
        print('pasword : ',password)
        print("User : ",user)
        if user and check_password(password, user.password):
            login(request, user)
            print('You are authenticated buddy !!!!!!!')
            return redirect('home_page')  # Redirect to the home page
        else:
            # Handle invalid credentials
            messages.error(request, 'Invalid email or password.')
            return redirect('login_page')

    return render(request, 'login.html')

# @login_required(login_url="login_page")
def home_page(request):
    user_email = request.session.get('user_email')
    print("Inside Home Page")
    print("session user email", user_email)
    user = Person.objects.filter(email=user_email).first()
    if user is None:
        return redirect('login_page')
    bank_details = BankDetails.objects.filter(user=user).first()
    context = {
        'profile': user,
        'bank_details': bank_details  # Pass bank details to the template
    }
    
    return render(request, 'home.html', context)