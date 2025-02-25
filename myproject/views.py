from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from myproject.models import CustomUser  # Import your CustomUser model


def index(request):
    return render(request, 'index.html')

def SphereAi(request):
    return render(request, 'SphereAi.html')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        phone = request.POST.get('phone')

        # Validation
        if not email:
            messages.error(request, "Email is required.")
            return redirect('signup')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "User with this email already exists.")
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        # Create user using the correct field names
        user = CustomUser.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Save phone number if provided
        if phone:
            user.phone = phone
            user.save()

        messages.success(request, "User registered successfully!")
        return redirect('login')

    return render(request, 'signup.html')


def login(request):
    User = get_user_model()  # Get the custom user model
    user_count = User.objects.count()  # Count all entries

    print(f"Total users: {user_count}")
    return render(request, 'login.html')

def planConfirmation(request):
    return render(request, 'planConfirmation.html')

def forgot(request):
    return render(request, 'forgot.html')

def creation(request):
    return render(request, 'UserCreation.html')