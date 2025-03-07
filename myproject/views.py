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
from PIL import Image, ImageStat
from io import BytesIO
### For Chat ###
import os
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


password_reset_tokens = {}


def index(request):
    return render(request, 'index.html', {"user": request.user})

def planPage(request):
    return render(request, 'planPage.html')



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
            return redirect('forgot')

        reset_token = get_random_string(32)
        password_reset_tokens[reset_token] = email  # Store token temporarily
        reset_link = request.build_absolute_uri(reverse('password_reset_confirm', args=[reset_token]))

        send_mail(
            'Password Reset Request',
            f'Click the link below to reset your password:\n{reset_link}',
            'no-reply@yourdomain.com',  # Change to your email
            [email],
            fail_silently=False,
        )
        print(reset_link)

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
            return redirect("password_reset_complete")
        except CustomUser.DoesNotExist:
            return render(request, "password_reset_confirm.html", {"error": "User not found."})

    return render(request, "password_reset_confirm.html", {"token": token})


def password_reset_complete(request):
    user = request.user
    interest = user.interests
    print("\nhello")
    print(user.username)
    print(str(len(interest)))
    print(user.location)

    for string in interest:
        print(string+"\n")
        print(user.username+"\n")
    return render(request, "password_reset_complete.html")

def creation(request):
    return render(request, 'UserCreation.html')

def about(request):
    return render(request, 'about.html')

def logout_view(request):
    logout(request)  # Logs the user out
    return redirect('index')  # Redirects to the index page

def get_restaurant_details(request):
    restaurant_name = request.GET.get("restaurantName")
    location = request.GET.get("location")

    if not restaurant_name or not location:
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    GOOGLE_API_KEY = settings.GOOGLE_API_KEY

    # Ensure location is valid before making API requests
    if location.strip() == "":
        return JsonResponse({"error": "Location cannot be empty"}, status=400)

    search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={restaurant_name}+{location}&key={GOOGLE_API_KEY}"
    search_response = requests.get(search_url).json()

    if "results" not in search_response or not search_response["results"]:
        return JsonResponse({"error": "No restaurant found"}, status=404)

    place_id = search_response["results"][0]["place_id"]
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,photos&key={GOOGLE_API_KEY}"
    details_response = requests.get(details_url).json()

    if "result" not in details_response:
        return JsonResponse({"error": "No details found"}, status=404)

    rating = details_response["result"].get("rating", "N/A")
    image_url = "../static/default.jpg"

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

@csrf_exempt
@login_required  # Ensures only logged-in users can generate a plan
def generate_date_plan(request):
    print(f"🔍 Received request: {request.method}")

    if request.method == "OPTIONS":
        return JsonResponse({"message": "CORS preflight successful"}, status=200)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        print("✅ POST request received")

        # ✅ Read and parse request data
        data = json.loads(request.body)
        print(f"📨 Received Data: {data}")

        # ✅ Validate required inputs
        required_fields = ["location", "date", "time", "attendees", "food", "ocasion", "order"]
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({"error": f"Missing required field: {field}"}, status=400)

        location = data["location"]
        date = data["date"]
        time = data["time"]
        attendees = data["attendees"]
        food = data["food"]
        ocasion = data["ocasion"]  # New field
        order = data["order"]  # New field

        # ✅ Get User Preferences from Database
        user = request.user  # Get logged-in user

        dietary_restrictions = user.diet_restrictions if user.diet_restrictions else "None"
        favorite_cuisines = user.favorite_cuisines if user.favorite_cuisines else "None"
        favorite_interests = user.interests if user.interests else "None"

        print(f"📌 Extracted User Preferences -> Dietary Restrictions: {dietary_restrictions}, Favorite Cuisines: {favorite_cuisines}, Favorite Interests: {favorite_interests}")

        # ✅ Check if OpenAI API key is set correctly
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return JsonResponse({"error": "OpenAI API Key is missing!"}, status=500)

        # ✅ OpenAI API Call with User Preferences and new fields
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Generate a JSON object for a **{ocasion}** date plan in {location} on {date} at {time} for {attendees} people, featuring {food} cuisine.

                    The user wants the order of the plan to be: **{order}**.

                    Take into account the user's saved preferences:
                    - **Dietary Restrictions:** {dietary_restrictions}
                    - **Favorite Cuisines:** {favorite_cuisines}
                    - **Favorite Interests for Activities:** {favorite_interests}

                    The JSON should contain:
                    - "date": string (formatted as YYYY-MM-DD)
                    - "time": string
                    - "guests": integer
                    - "location": string
                    - "cuisine": string
                    - "ocasion": string
                    - "order": string
                    - "restaurants": an **array of exactly 3 objects**, each with:
                        - "name": string
                        - "address": string
                        - "website": string
                        - "rating": float
                        - "reservation_time": string
                    - "events": an **array of exactly 3 objects**, each with:
                        - "name": string
                        - "address": string
                        - "website": string
                        - "start_time": string
                        - "end_time": string
                        - "type": string

                    **IMPORTANT RULES**:
                    - Respond **ONLY** with a JSON object, with **no explanations, disclaimers, or Markdown formatting**.
                    - Ensure **exactly 3 restaurants** and **exactly 3 events** are included.
                    - The selections must be **realistic, diverse, and match the user's saved preferences**.
                    - **Do NOT** use placeholders such as "Restaurant One" or "Event One."
                    - **Make Sure** that everything is in the radius of 10 miles or less only.
                    """
                }
            ],
            max_tokens=700,
            temperature=0.7,
        )

        chat_response = response.choices[0].message.content.strip()

        print(chat_response)

        # ✅ Ensure OpenAI response is in valid JSON format
        try:
            plan_data = json.loads(chat_response)

            # ✅ Extra Validation: Ensure OpenAI returns exactly 3 restaurants and 3 events
            if len(plan_data.get("restaurants", [])) != 3:
                print("⚠️ OpenAI did not return exactly 3 restaurants. Adjusting output.")
                plan_data["restaurants"] = plan_data.get("restaurants", [])[:3]

            if len(plan_data.get("events", [])) != 3:
                print("⚠️ OpenAI did not return exactly 3 events. Adjusting output.")
                plan_data["events"] = plan_data.get("events", [])[:3]

        except json.JSONDecodeError:
            print("❌ ERROR: OpenAI response is not valid JSON.")
            return JsonResponse({"error": "Invalid AI response format"}, status=500)

        return JsonResponse(plan_data, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format received"}, status=400)

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def update_user_profile(request):
    if request.method == 'POST':
        user = request.user

        user.location = request.POST.get('location', user.location)
        user.occupation = request.POST.get('occupation', user.occupation)
        user.biography = request.POST.get('biography', user.biography)
        # Handle JSON fields safely
        try:
            interests = request.POST.get("interests")
            if interests:
                interests = json.loads(interests)  # Convert JSON string to a Python list
                user = request.user
                user.interests = interests  # Directly store the list in JSONField
                user.save()
                user.favorite_cuisines = json.loads(request.POST.get('favorite_cuisines', '[]'))
                user.diet_restrictions = json.loads(request.POST.get('diet_restrictions', '[]'))
        except json.JSONDecodeError:
            user.interests, user.favorite_cuisines, user.diet_restrictions = [], [], []


        # Handle profile picture upload
        profile_picture = request.FILES.get('picture', None)

        # Debugging Statements
        print("🔹 DEBUG: User Profile Data Before Saving:")
        print(f"   - User: {user.username} (ID: {user.id})")
        print(f"   - Location: {user.location}")
        print(f"   - Occupation: {user.occupation}")
        print(f"   - Biography: {user.biography}")
        print(f"   - Interests: {user.interests}")
        print(f"   - Favorite Cuisines: {user.favorite_cuisines}")
        print(f"   - Diet Restrictions: {user.diet_restrictions}")
        print(f"   - Profile Picture Uploaded: {'Yes' if profile_picture else 'No'}")


        if profile_picture:
            user.picture = profile_picture

        # Save user data
        user.save()
        print("✅ User profile successfully updated!\n")

        return redirect('index')

    return render(request, 'UserCreation.html')


@csrf_exempt
def get_location_image(request):
    google_api_key = os.getenv("GOOGLE_API_KEY")  # Fetch API Key from .env
    city = request.GET.get("city", "Chicago")  # Default city

    if not google_api_key:
        return JsonResponse({"error": "Google API key not found"}, status=500)

    # Fetch Place ID
    place_search_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": city,
        "inputtype": "textquery",
        "fields": "place_id",
        "key": google_api_key,
    }

    place_response = requests.get(place_search_url, params=params)
    place_data = place_response.json()

    if "candidates" not in place_data or not place_data["candidates"]:
        return JsonResponse({"error": "Place not found"}, status=404)

    place_id = place_data["candidates"][0]["place_id"]

    # Fetch Place Details (Get photos)
    place_details_url = f"https://maps.googleapis.com/maps/api/place/details/json"
    details_params = {
        "place_id": place_id,
        "fields": "photo",
        "key": google_api_key,
    }

    details_response = requests.get(place_details_url, params=details_params)
    details_data = details_response.json()

    if "result" not in details_data or "photos" not in details_data["result"]:
        return JsonResponse({"error": "No images found"}, status=404)

    # Get highest quality photo reference
    photo_references = details_data["result"]["photos"]

    if not photo_references:
        return JsonResponse({"error": "No images available"}, status=404)

    # Choose the **best** image (first in the list)
    photo_reference = photo_references[0]["photo_reference"]
    image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photoreference={photo_reference}&key={google_api_key}"

    return JsonResponse({"image_url": image_url})

@login_required
def profileEdit(request):
    user = request.user  # Get the logged-in user

    # Ensure JSON fields are properly loaded as lists
    def parse_json_field(field):
        if isinstance(field, str):  # Only load if it's a string
            try:
                return json.loads(field)
            except json.JSONDecodeError:
                return []  # Return empty list if decoding fails
        elif isinstance(field, list):  # If already a list, return as-is
            return field
        return []  # Default to empty list

    interests = parse_json_field(user.interests)
    favorite_cuisines = parse_json_field(user.favorite_cuisines)
    diet_restrictions = parse_json_field(user.diet_restrictions)

    context = {
        "user": user,
        "interests": interests,
        "favorite_cuisines": favorite_cuisines,
        "diet_restrictions": diet_restrictions,
    }
    
    return render(request, 'profileEdit.html', context)