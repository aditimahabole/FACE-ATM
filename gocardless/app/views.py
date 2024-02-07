from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Person , BankDetails
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from urllib.parse import urlencode
from django.contrib.auth.models import User
import os

from django.shortcuts import get_object_or_404


# def home_page(request):
#     print('Inside Home Page')
#     email = request.GET.get('email')
#     print('person email', email)
#     user = request.user
#     profile = None
#     if user.is_authenticated:
#         profile = get_object_or_404(Person, email=user.email)
#     if request.method == 'POST':  # Changed from '==' to 'method' to check the method of the request
#         print('HELLO')
    
    # return render(request, 'home.html', {'profile': profile})
    
    

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
        if Person.objects.filter(email=email).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register_page')
        hashed_password = make_password(password)

        # Create the user instance
        user = Person.objects.create(
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
    if request.method == 'POST':
        print('Inside POST method')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email).first()
        print("User:", user)
        
        # Authenticate the user
        hashed_password = make_password(password)
        authenticated_user = authenticate(request, email=email, password=password)
        print(authenticated_user)
        if authenticated_user:
            print("User authenticated successfully")
            login(request, authenticated_user)
            return redirect('home_page')  # Redirect to the home page
        else:
            print("Invalid email or password")
            # Handle invalid credentials
            messages.error(request, 'Invalid email or password.')
            return redirect('login_page')

    print("Rendering login page")
    return render(request, 'login.html')



# def login_page(request):
    
#     if request.method == 'POST':
#         print('inside if')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         user = Person.objects.filter(email=email).first()
#         print("User : ",user)
#         if user and check_password(password, user.password):
#             login(request, user)
#             return redirect('home_page')  # Redirect to the home page
#         else:
#             # Handle invalid credentials
#             messages.error(request, 'Invalid email or password.')
#             return redirect('login_page')

#     return render(request, 'login.html')

@login_required(login_url='login_page')
def home_page(request):
    print('request ',request.user)
    print("Inside Home Page")

    profile = None
    if request.user.is_authenticated:
        print("yes authenticated")
        profile = Person.objects.get(email=request.user.email)
        print("profile is ",profile)
        profile = get_object_or_404(Person, email=request.user.email)
        print("Profile : ",profile)
    
    
    return render(request, 'home.html')