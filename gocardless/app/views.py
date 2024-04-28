from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Person , BankDetails
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from dotenv import load_dotenv
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
import cv2
import face_recognition
import numpy as np
import pandas as pd
import csv
from datetime import datetime
from django.http import JsonResponse
import time
load_dotenv()
# ---------------------------FOR OTP---------------------------
from django.core.exceptions import SuspiciousOperation
from django.contrib.sessions.backends.db import SessionStore

# --------------------OTP PART------------------------------
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode
from twilio.rest import Client
# -------------------------TRANSACTION-------------------------
from django.shortcuts import render
from django.http import JsonResponse
from .models import Person, BankDetails

def transaction(request):
    if request.method == 'POST':
        withdraw_amount = float(request.POST.get('withdraw_amount'))
        email = request.session.get('email')
        phone = request.session.get('phone')
        try:
            user = Person.objects.get(email=email)
        except Person.DoesNotExist:
            print("USER NOT EXIST")
            
            
            return JsonResponse({'status': 'error', 'message': 'User not found'})
        try:
            bank_details = BankDetails.objects.get(user=user)
        except BankDetails.DoesNotExist:
            print("NO BANK DETAIL")
            
            return JsonResponse({'status': 'error', 'message': 'Bank details not found'})
        if withdraw_amount > bank_details.current_balance:
            print("TOO MUCH MONEY")
            
            return JsonResponse({'status': 'error', 'message': 'Not enough money in the account'})
        print("HURRAY")
        bank_details.current_balance -= withdraw_amount
        bank_details.save()
        print(bank_details)
        
        return JsonResponse({'status': 'success', 'message': 'Transaction completed successfully'})
    return render(request, 'transaction.html')

# --------------------------------------------------------------
def generate_otp():
    # Generate 4-digit OTP
    otp = random.randint(1000, 9999)
    return str(otp)
# -----------------------SEND EMAIL OTP--------------------------
from email.mime.text import MIMEText
import smtplib
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse

def send_email_otp(request):
    email = request.session.get('email')
    phone = request.session.get('phone')
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Please Login first.'})
    otp = generate_otp()
    smtp_server =  os.getenv('SMTP_SERVER')
    smtp_port =  os.getenv('SMTP_PORT')
    email_sender =  os.getenv('EMAIL_SENDER')
    email_password = os.getenv('EMAIL_PASSWORD')

    try:
        validate_email(email)
    except ValidationError:
        
        return JsonResponse({'status': 'error', 'message': 'Invalid email'})
    message = MIMEText(f'Your OTP is: {otp}')
    message['Subject'] = 'FACE-ATM : Your OTP'
    message['From'] = email_sender
    message['To'] = email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_sender, email_password)
        server.sendmail(email_sender, [email], message.as_string())
        server.quit()
        
        request.session['otp'] = otp
        request.session.save()
    except Exception as e:
        
        return JsonResponse({'status': 'error', 'message': 'Please Login first.'})
    
    return JsonResponse({'status': 'success', 'message': 'OTP sent to email','email':email,'phone':phone})

# -------------------------SEND SMS OTP--------------------------------
from twilio.rest import Client
import os

def send_sms_otp(request):
    print('inside SMS OTP')
    email = request.session.get('email')
    phone = request.session.get('phone')
  
    otp = generate_otp()
    message_body = f'FACE_ATM Your OTP is: {otp}'

    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
    print('Twilio Phone : ',twilio_number)
    
    try:
        request.session['otp'] = otp
        request.session.save()
        client = Client(account_sid, auth_token)
        
        print('Attempting to send message...')
        message = client.messages.create(
            body = message_body,
            from_ =twilio_number,
            to = phone
        )
        
        print("Message sent successfully: ", message.sid)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': 'Failed to send OTP.'})
    
    return JsonResponse({'status': 'success', 'message': 'OTP sent to phone number', 'email': email, 'phone': phone})

# -----------------------VERIFY OTP--------------------------------------
from django.contrib.sessions.backends.db import SessionStore
from django.http import JsonResponse

def verify_otp(request):
    entered_otp = request.GET.get('otp')
    if entered_otp == "":
        
        return JsonResponse({'status': 'empty', 'message': 'Please Enter OTP'})
        
    session_key = request.session.session_key
    if not session_key:
        return JsonResponse({'status': 'error', 'message': 'Session key not found'})

    session = SessionStore(session_key)
    stored_otp = session.get('otp')
    if not stored_otp:
        
        return JsonResponse({'status': 'error', 'message': 'OTP not found in session'})

    
    if entered_otp == stored_otp:
        del session['otp']
        session.save()
        
        return JsonResponse({'status': 'success', 'message': 'OTP verified successfully'})
    else:
        
        return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})


# -------------------------------IMAGE PART------------------------------
def save_photos_encodings(image_path):
    

    known_faces_file = 'known_faces.xlsx'
    known_face_encodings = []
    known_face_names = []

    if os.path.exists(known_faces_file):
        df_known_faces = pd.read_excel(known_faces_file)
        known_face_encodings = df_known_faces['Face Encoding'].tolist()
        known_face_names = df_known_faces['Face Name'].tolist()

    
    full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
    
    image = face_recognition.load_image_file(full_image_path)
    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) > 0:
        
        new_encoding = face_encodings[0]
        if new_encoding not in known_face_encodings:
            known_face_encodings.append(new_encoding)
            known_face_names.append(os.path.splitext(os.path.basename(image_path))[0])
            print(f"Face encoding added for {known_face_names[-1]}")
        else:
            print("Face encoding already exists for", known_face_names[-1])
    else:
        print("No face found in", image_path)

    
    df_new_faces = pd.DataFrame(data={'Face Name': known_face_names, 'Face Encoding': known_face_encodings})
    if os.path.exists(known_faces_file):
        df_combined = pd.concat([df_known_faces, df_new_faces], ignore_index=True)
    else:
        df_combined = df_new_faces

    df_combined.to_excel(known_faces_file, index=False)
    print(f"Face encodings saved to '{known_faces_file}'")
# -----------------------------------MATCH PERSON------------------------
def match_person(request):
    df_known_faces = pd.read_excel('known_faces.xlsx')
    known_face_encodings = [np.fromstring(encoding.strip('[]'), dtype=float, sep=' ') for encoding in df_known_faces['Face Encoding']]
    known_face_names = df_known_faces['Face Name'].tolist()
    users = known_face_names.copy()
    
    match_found = False
    video_capture = None
    
    try:
        video_capture = cv2.VideoCapture(0)
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        csv_file_name = current_date + '_matches.csv'
        with open(csv_file_name, 'w', newline='') as f:
            line_writer = csv.writer(f)
            while not match_found:
                print("READING")
                ret, frame = video_capture.read()

                if not ret:
                    print("Error: Could not capture frame.")
                    break

                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                if len(face_locations) > 0:
                    for face_encoding in face_encodings:
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = ""

                        if True in matches:
                            first_match_index = matches.index(True)
                            name = known_face_names[first_match_index]
                            if name in users:
                                match_found = True
                                print('User removed:', name)
                                users.remove(name)
                                current_time = now.strftime("%H-%M-%S")
                                line_writer.writerow([name, current_time])
                                print("User is removed lets end")
                                break
                            
                print("SHOWING")
                cv2.imshow('Video', frame)
                key = cv2.waitKey(1)
                if key & 0xFF == ord('q') or (request.GET.get('action') == 'stop' and match_found):
                    break

        if match_found:
            print("Recognition ended. User recorded:", name)
            email, phone = name.split("_")[:2]
            
            return JsonResponse({'match_found': True, 'email': email, 'phone': phone})
        elif not match_found:
            print("Recognition ended. User not found.")
            return JsonResponse({'match_found': False})
    finally:
        if video_capture is not None:
            print("----------Video Released---------")
            video_capture.release()
            cv2.destroyAllWindows()
# ------------------------------ OTP-------------------------------------
def otp(request):
    print("INSIDE OTP PAGE")
    # email = request.GET.get('email')
    # phone = request.GET.get('phone')
    email = request.session.get('email')
    phone = request.session.get('phone')
    context = {
        'email': email,
        'phone': phone
    }
    print(context)
    
    return render(request, 'otp.html',context)
# ----------------------------REGISTER-------------------------------
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
        
        
        
        if Person.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register_page')
        if Person.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('register_page')
        hashed_password = make_password(password)
        user = Person.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
            contact=contact,
            age=age
        )

        
        if image:
            print("saving image")
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = f"{email}_{contact}_{first_name}.png" 
            print("filename : ", filename)
            img = Image.open(image)
            image_stream = io.BytesIO()
            img.save(image_stream, format='PNG')  # Convert and save as PNG
            fs.save(filename, image_stream)
            user.image = fs.url(filename)
            print("user image : ", user.image)
            print("save encodings is called bro")
            image_path = str(filename)
            print(image_path)
            save_photos_encodings(filename)
            print("save encodings ENDS")

        bank_details = BankDetails.objects.create(
            user=user,
            bank_name=bank_name,
            account_number=account_number,
        )

        
        user.save()
        bank_details.save()

        messages.success(request, 'Account created successfully!')
        return redirect('login_page')

    return render(request, 'register.html')
# ----------------------------LOGIN PAGE-----------------------------
from django.contrib.auth import authenticate
def login_page(request):
    print("INSIDE LOGIN")
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = Person.objects.filter(email=email).first()
        print('LOGIN CONTACT', user.contact)
        print('LOGIN EMAIL', user.email)
        # session created
        
        
        if user and check_password(password, user.password):
            user1 = authenticate(request, username=user.username, password=password)
            request.session['email'] = user.email
            request.session['phone'] = user.contact
            return redirect('home_page')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login_page')

    return render(request, 'login.html')

# -----------------------------HOMEPAGE------------------------------
def home_page(request):
    user_email = request.session.get('email')
    print("Inside Home Page")
    print("session user email", user_email)
    user = Person.objects.filter(email=user_email).first()
    if user is None:
        return redirect('login_page')
    bank_details = BankDetails.objects.filter(user=user).first()
    context = {
        'profile': user,
        'bank_details': bank_details 
    }
    
    return render(request, 'home.html', context)
# ---------------------------------LOGOUT--------------------------
def logout(request):
    # Delete session variables
    print("SESSION DELEETDDDDDDD")
    if 'email' in request.session:
        del request.session['email']
    if 'phone' in request.session:
        del request.session['phone']
    some = request.session.get('email')
    print('EMAIL ? ', some)
    print("END")
    return JsonResponse({'status': 'success', 'message': 'Logged out successfully'})
# ---------------------------------------END-------------------------