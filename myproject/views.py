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

def signup(request):
    if request.method == 'POST':
        # Get email, password, and confirm password from form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        phone = request.POST.get('phone')



    # Check if email is provided
        if not email:
            messages.error(request, "Email is required.")
            return render(request, 'user_signup.html')

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "User with this email already exists")
            return render(request, 'user_signup.html')

        # Create user using django's built-in User model
        user = User.objects.create_user(
            username=username,
            password=password,
            Fname=fname,
            Lname=lname,
            Phone=phone
        )

        messages.success(request, "User created successfully!")
        return redirect('login')
    else:
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