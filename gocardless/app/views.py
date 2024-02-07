from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Person , BankDetails
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
from django.shortcuts import get_object_or_404

# from match_person import match_person
# --------------------REGISTER PAGE-----------------------------


def register_page(request):
    if request.method == "POST":
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

        # Check if the username already exists
        username = email  # Assuming email will be used as the username
        if Person.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register_page')

        # Hash the password
        hashed_password = make_password(password)

        # Create the user instance
        user = Person.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=hashed_password,
            contact=contact,
            age=age
        )

        # Save the uploaded image
        # if image:
        #     fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        #     filename = fs.save(image.name, image)
        #     user.image = fs.url(filename)

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

        messages.success(request, 'Account created successfully!')
        return redirect('login_page')

    return render(request, 'register.html')


# --------------------LOGIN PAGE-----------------------------
def login_page(request):
    print('Inside Login page')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Retrieve the user from the database based on the email
        user = Person.objects.filter(email=email).first()

        # Check if the user exists and if the provided password matches the hashed password
        if user and check_password(password, user.password):
            # If the password matches, log in the user
            login(request, user)
            # Redirect to a success page.
            print("Success!")
            return redirect('home_page')
        else:
            print("Failure!")
            # If the password doesn't match or the user doesn't exist, display an error message.
            messages.error(request, 'Invalid email or password.')
            return redirect('login_page')

    return render(request, 'login.html')

def home_page(request):
    print('Inside Home Page')
    if request.method == 'POST':
        # match_person()
        print('start')
    
    return render(request, 'home.html')