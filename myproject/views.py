from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from myproject.models import CustomUser  # Import your CustomUser model
from django.contrib.auth import authenticate, login



def index(request):
    return render(request, 'index.html')

def SphereAi(request):
    if request.user.is_authenticated:
        print(f"Logged-in User: {request.user.username}")  # Print username to console
    else:
        print("No user is logged in.")  # If no user is logged in

    return render(request, 'SphereAi.html')


def home(request):
    return render(request, 'SphereAi.html')

def signup(request):
    print("Request method:", request.method)  # Debugging

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


def user_login(request):  # Renamed function
    print("Request method:", request.method)  # Debugging

    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the user is logging in with email or username
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(email=username_or_email)
            username = user.username  # Use username if email is entered
        except User.DoesNotExist:
            username = username_or_email  # Use entered username if not found by email

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')  # Redirect to homepage
        else:
            messages.error(request, "Invalid email/username or password.")
            return redirect('login')

    return render(request, 'login.html')



def planConfirmation(request):
    return render(request, 'planConfirmation.html')

def forgot(request):
    return render(request, 'forgot.html')

def creation(request):
    return render(request, 'UserCreation.html')