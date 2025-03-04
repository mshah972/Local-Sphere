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
### For Chat ###
import os
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


from myproject.models import CustomUser  # Ensure CustomUser model is imported correctly


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
    return render(request, 'forgot.html')


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
    image_url = "https://via.placeholder.com/150"

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

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import openai
import os

@csrf_exempt
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
        required_fields = ["location", "date", "time", "attendees", "food"]
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({"error": f"Missing required field: {field}"}, status=400)

        location = data["location"]
        date = data["date"]
        time = data["time"]
        attendees = data["attendees"]
        food = data["food"]

        print(f"📌 Extracted Inputs -> Location: {location}, Date: {date}, Time: {time}, Attendees: {attendees}, Food: {food}")

        # ✅ Check if OpenAI API key is set correctly
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return JsonResponse({"error": "OpenAI API Key is missing!"}, status=500)

        # ✅ OpenAI API Call with strict JSON format enforcement
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Generate a JSON object for a date plan in {location} on {date} at {time} for {attendees} people, featuring {food} cuisine.
                    
                    The JSON should contain:
                    - "date": string (formatted as YYYY-MM-DD)
                    - "time": string
                    - "guests": integer
                    - "location": string
                    - "cuisine": string
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

                    ⚠️ **STRICT RULES**:
                    - Respond **ONLY** with a JSON object, with **no explanations, disclaimers, or Markdown formatting**.
                    - Ensure **exactly 3 restaurants** and **exactly 3 events** are included.
                    """
                }
            ],
            max_tokens=600,
            temperature=0.7,
        )

        chat_response = response.choices[0].message.content.strip()

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

        # Handle multiple selections for interests, cuisines, and diet restrictions
        user.interests = json.loads(request.POST.get('interests', '[]'))
        user.favorite_cuisines = json.loads(request.POST.get('favorite_cuisines', '[]'))
        user.diet_restrictions = json.loads(request.POST.get('diet_restrictions', '[]'))

        # Handle profile picture upload
        if 'picture' in request.FILES:
            user.picture = request.FILES['picture']

        user.save()
        return redirect('index')

    return render(request, 'UserCreation.html')