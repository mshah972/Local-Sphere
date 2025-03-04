import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.urls import reverse
from myproject.models import CustomUser  # Ensure CustomUser model is imported correctly
from django.contrib.auth.hashers import make_password


password_reset_tokens = {}


def index(request):
    return render(request, 'index.html', {"user": request.user})


def SphereAi(request):
    if request.user.is_authenticated:
        print(f"Logged-in User: {request.user.username}")  # Debugging
    else:
        print("No user is logged in.")  # Debugging

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
        if phone!= '':
            if len(phone) != 10 or not phone.isnumeric():
                messages.error(request, "Telephone is invalid")
                return redirect('signup')
        # Create user
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

        # Authenticate and log in the user
        new_user = authenticate(username=username, password=password)
        if new_user:
            login(request, new_user) 

        return redirect('creation') 

    return render(request, 'signup.html')


def user_login(request):  # Fixed function name
    print("Request method:", request.method)  # Debugging
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the user is logging in with email or username
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
            return redirect('index')  # Redirect to index (homepage)
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')


@login_required
def my_account(request):
    """ User account page. Requires authentication. """
    return render(request, 'my_account.html', {"user": request.user})


def planConfirmation(request):
    return render(request, 'planConfirmation.html')


def forgot(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect('forgot')

        reset_token = get_random_string(32)
        password_reset_tokens[reset_token] = email  # Store token temporarily
        reset_link = request.build_absolute_uri(reverse('password_reset_confirm', args=[reset_token]))

        #send_mail(
           # 'Password Reset Request',
          #  f'Click the link below to reset your password:\n{reset_link}',
        #    'no-reply@yourdomain.com',  # Change to your email
         #   [email],
        #    fail_silently=False,
        #)
        print(reset_link)

        messages.success(request, "Reset link sent.")
        return redirect('forgot')

    return render(request, 'forgot.html')
def password_reset_confirm(request, token):
    email = password_reset_tokens.get(token)
    if not email:
        return render(request, "password_reset_confirm.html", {"error": "Invalid or expired token."})

    if request.method == 'POST':
        new_password = request.POST.get("newpassword")
        confirm_password = request.POST.get("confirmnewpassword")



        if new_password != confirm_password:
            return render(request, "password_reset_confirm.html", {"token": token, "error": "Passwords do not match."})

        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()
            del password_reset_tokens[token]  # Remove used token
            messages.success(request, "Password reset successfully.")
            return redirect("password_reset_complete")
        except CustomUser.DoesNotExist:
            return render(request, "password_reset_confirm.html", {"error": "User not found."})

    return render(request, "password_reset_confirm.html", {"token": token})


def password_reset_complete(request):
    return render(request, "password_reset_complete.html")

def creation(request):
    return render(request, 'UserCreation.html')

def logout_view(request):
    logout(request)  # Logs the user out
    return redirect('index')  # Redirects to the index page

def get_restaurant_details(request):
    restaurant_name = request.GET.get("restaurantName")
    location = request.GET.get("location")

    if not restaurant_name or not location:
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    GOOGLE_API_KEY = settings.GOOGLE_API_KEY  # Store in settings.py for security

    # Step 1: Find restaurant using Google Places Text Search API
    search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={restaurant_name}+{location}&key={GOOGLE_API_KEY}"
    search_response = requests.get(search_url).json()

    if "results" not in search_response or not search_response["results"]:
        return JsonResponse({"error": "No restaurant found"}, status=404)

    place_id = search_response["results"][0]["place_id"]

    # Step 2: Get details (rating + photos)
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,photos&key={GOOGLE_API_KEY}"
    details_response = requests.get(details_url).json()

    if "result" not in details_response:
        return JsonResponse({"error": "No details found"}, status=404)

    # Extract rating
    rating = details_response["result"].get("rating", "N/A")

    # Extract first image if available
    image_url = "https://images.unsplash.com/photo-1498837167922-ddd27525d352?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    if "photos" in details_response["result"]:
        photo_ref = details_response["result"]["photos"][0]["photo_reference"]
        image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=600&photo_reference={photo_ref}&key={GOOGLE_API_KEY}"

    return JsonResponse({"rating": rating, "imageUrl": image_url})

def get_google_maps_api_key(request):
    return JsonResponse({"apiKey": settings.GOOGLE_API_KEY})

def get_mapbox_api_key(request):
    """API endpoint to securely return Mapbox API key."""
    if not settings.MAPBOX_ACCESS_TOKEN:
        return JsonResponse({"error": "Mapbox API Key not found"}, status=500)

    return JsonResponse({"mapboxApiKey": settings.MAPBOX_ACCESS_TOKEN})