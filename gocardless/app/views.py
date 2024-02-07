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



# --------------------REGISTER PAGE-----------------------------


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
        routing_number = request.POST.get('routing_number')
        if Person.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register_page')
        if Person.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('register_page')
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


        # Save the uploaded image
        if image:
            print("image is : ",image)
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            print("fs is : ",fs)
            print("file name is : ",image.name)
            filename = fs.save(image.name, image)
            user.image = fs.url(filename)

        # Save bank details
        bank_details = BankDetails.objects.create(
            user=user,
            bank_name=bank_name,
            account_number=account_number,
            routing_number=routing_number
        )

        # Save the user and bank details
        user.save()
        bank_details.save()
        print("User Created : ",user)
        print("Bank Details : ",bank_details)

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