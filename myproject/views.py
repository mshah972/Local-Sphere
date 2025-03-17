import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.urls import reverse
from myproject.models import CustomUser  # Ensure CustomUser model is imported correctly
from django.contrib.auth.hashers import make_password
from PIL import Image, ImageStat
from io import BytesIO
from datetime import datetime
### For Chat ###
import os
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from dotenv import load_dotenv
from myproject.models import PlanConfirmation  # Ensure CustomUser model is imported correctly
import re  # Import the re module

DEFAULT_IMAGE_URL = "https://images.unsplash.com/photo-1494522358652-f30e61a60313?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"



load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


password_reset_tokens = {}


def index(request):
    return render(request, 'index.html', {"user": request.user})

def planPage(request):
    return render(request, 'planPage.html')

def quickSphere(request):
    return render(request, 'quickSphere.html')


def SphereAi(request):
    if request.user.is_authenticated:
        print(f"Logged-in User: {request.user.username}")  # Debugging
    else:
        print("No user is logged in.")  # Debugging

    return render(request, 'SphereAi.html')

@login_required
def SphereAi(request):
    user = request.user

    # Fetch user preferences from the database
    favorite_foods = ", ".join(user.favorite_cuisines) if user.favorite_cuisines else "None"
    dietary_restrictions = ", ".join(user.diet_restrictions) if user.diet_restrictions else "None"
    interests = ", ".join(user.interests) if user.interests else "None"

    context = {
        "favorite_foods": favorite_foods,
        "dietary_restrictions": dietary_restrictions,
        "interests": interests,
    }
    return render(request, "SphereAi.html", context)


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

def format_date_readable(date_obj):
    """Format date into 'Saturday, March 8th' style"""
    day = date_obj.strftime("%d").lstrip("0")  # Remove leading zero
    day_with_suffix = f"{day}{get_ordinal_suffix(int(day))}"  # Add suffix
    return date_obj.strftime("%A, %B ") + day_with_suffix

def get_ordinal_suffix(day):
    """Get ordinal suffix for a given day (1st, 2nd, 3rd, 4th, etc.)"""
    if 10 <= day % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

def save_plan_selection(request):
    print("hello")

    if request.method == "POST":
        print("hello")
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        try:
            data = json.loads(request.body)
            time_pattern = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
            time = data.get("time")
            if not time or not time_pattern.match(time):
                time = None

            guests = data.get("guests")
            if not isinstance(guests, int) or guests < 1:
                guests = None
            restaurant_name = data.get("restaurant", {}).get("name")  # ✅ Fixed
            print(restaurant_name)

            restaurant_data = data.get("restaurant", {})  # ✅ Extract restaurant data safely
            event_data = data.get("event", {})

            restaurant_name = restaurant_data.get("name")
            restaurant_address = restaurant_data.get("address")
            restaurant_longitude = restaurant_data.get("longitude")
            restaurant_latitude = restaurant_data.get("latitude")
            restaurant_image = restaurant_data.get("image_url", DEFAULT_IMAGE_URL)  # ✅ Use default image if missing

            event_name = event_data.get("name")
            event_address = event_data.get("address")
            event_longitude = event_data.get("longitude")
            event_latitude = event_data.get("latitude")
            event_image = event_data.get("image_url", DEFAULT_IMAGE_URL)  # ✅ Use default image if missing

            raw_date = data.get("date")
            plan_date = None
            formatted_date = None
            if raw_date:
                try:
                    plan_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
                    formatted_date = format_date_readable(plan_date)
                except ValueError:
                    return JsonResponse({"error": "Invalid date format"}, status=400)

            plan = PlanConfirmation.objects.create(
                user=request.user,  # Associate plan with logged-in user
                date=plan_date,
                formatted_date=formatted_date,
                restaurant_name=restaurant_name,
                restaurant_address=restaurant_address,
                restaurant_longitude=restaurant_longitude,
                restaurant_latitude=restaurant_latitude,
                restaurant_image=restaurant_image,  # ✅ Save restaurant image

                event_name=event_name,
                event_address=event_address,
                event_longitude=event_longitude,
                event_latitude=event_latitude,
                event_image=event_image,  # ✅ Save event image

                time=time,
                occasion=data.get("occasion"),
                guests=guests,

            )

            plan.title = generate_plan_title(plan)
            plan.save()

            return JsonResponse({
                "message": "Plan saved successfully",
                "plan_id": plan.id,
                "redirect_url": "/profilePage/"  # Include redirect URL
            }, status=201)


        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

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

@login_required()
def profilePage(request):
    plans = PlanConfirmation.objects.filter(user=request.user).values(
        "id", "date", "time", "guests", "occasion", "order",
        "restaurant_name", "restaurant_address",
        "event_name", "event_address", "restaurant_latitude", "restaurant_longitude",
        "event_latitude", "event_longitude"
    )
    plans_list = list(plans)

    # Print the formatted JSON to the console
    print(json.dumps(plans_list, indent=4, default=str))
    return render(request, 'profilePage.html')

@login_required()
def get_restaurant_booking(request):
    """Fetch booking times for a restaurant from Yelp API"""
    restaurant_name = request.GET.get("name")  # Get restaurant name from request
    location = request.GET.get("location", "Chicago")  # Default to Chicago

    print(f"🔍 Fetching Yelp Booking for: {restaurant_name}")  # ✅ Debugging

    if not restaurant_name:
        return JsonResponse({"error": "Restaurant name is required"}, status=400)

    # Yelp API Endpoint
    url = f"https://api.yelp.com/v3/businesses/search?term={restaurant_name}&location={location}&limit=1"

    headers = {
        "Authorization": f"Bearer {settings.YELP_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        print("📜 Yelp API Response:", data)  # ✅ Debugging API Response

        # Extract restaurant ID
        businesses = data.get("businesses", [])
        if not businesses:
            return JsonResponse({"error": "Restaurant is not on Yelp!"}, status=404)

        restaurant_id = businesses[0]["id"]

        # Fetch booking availability using restaurant ID
        booking_url = f"https://api.yelp.com/v3/businesses/{restaurant_id}/reservations"

        return JsonResponse({"booking_url": booking_url, "restaurant": restaurant_name})

    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def get_user_plans(request):
    """Retrieve all saved plans for the authenticated user"""
    try:
        # ✅ Fetch all plans for the logged-in user
        user_plans = PlanConfirmation.objects.filter(user=request.user).order_by("-id")

        total_plans = user_plans.count()

        google_api_key = os.getenv("GOOGLE_API_KEY")


        # ✅ Convert QuerySet to JSON-friendly format
        plans_data = [
            {
                "id": plan.id,
                "title": plan.title,
                "date": plan.formatted_date if plan.formatted_date else plan.date.strftime("%Y-%m-%d") if plan.date else "No Date Set",
                "time": plan.time,
                "guests": plan.guests,
                "occasion": plan.occasion,
                "restaurant": {
                    "name": plan.restaurant_name,
                    "address": plan.restaurant_address,
                },
                "event": {
                    "name": plan.event_name,
                    "address": plan.event_address,
                },
                "image_url": plan.event_image or DEFAULT_IMAGE_URL,
            }
            for plan in user_plans
        ]

        # ✅ Return JSON response
        return JsonResponse({
            "plans": plans_data,
            "total_plans": total_plans
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required()
def plan_detail_view(request, plan_id):
    """Retrieve and display a specific plan based on the ID"""
    plan = get_object_or_404(PlanConfirmation, id=plan_id, user=request.user)

    return render(request, "planPage.html", {"plan_id": plan_id})

# Default fallback image

@login_required
def get_plan_details(request, plan_id):
    """Retrieve details of a specific plan including images"""
    try:
        print(f"🔍 Fetching Plan ID: {plan_id} for user: {request.user}")

        plan = get_object_or_404(PlanConfirmation, id=plan_id, user=request.user)

        plan_data = {
            "id": plan.id,
            "title": plan.title,
            "date": plan.date.strftime("%Y-%m-%d") if plan.date else "No Date Set",
            "time": plan.time.strftime("%H:%M") if plan.time else "No Time Set",
            "guests": plan.guests or 1,
            "occasion": plan.occasion or "No Occasion",
            "restaurant": {
                "name": plan.restaurant_name or "Unknown Restaurant",
                "address": plan.restaurant_address or "Unknown Address",
                "latitude": plan.restaurant_latitude,
                "longitude": plan.restaurant_longitude,
                "image_url": plan.restaurant_image or DEFAULT_IMAGE_URL,
            },
            "event": {
                "name": plan.event_name or "No Event",
                "address": plan.event_address or "No Event Address",
                "latitude": plan.event_latitude,
                "longitude": plan.event_longitude,
                "image_url": plan.event_image or DEFAULT_IMAGE_URL,
            },
        }

        print(f"✅ Returning Plan Data: {plan_data}")
        return JsonResponse(plan_data, status=200)

    except Exception as e:
        print(f"❌ Error retrieving plan: {e}")
        return JsonResponse({"error": str(e)}, status=500)

def delete_plan(request, plan_id):
    if request.method == "POST":
        plan = PlanConfirmation.objects.filter(id=plan_id)
        plan.delete()
        return JsonResponse({"success": True, "message": "Plan deleted successfully."})
    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)


def generate_plan_title(plan):
    """Generate a creative title using ChatGPT AI if not already saved."""

    # ✅ Check if a title already exists
    if plan.title:
        print(f"🔹 Using Existing Title: {plan.title}")  # Debugging
        return plan.title

    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=openai_api_key)

    prompt = f"""
    Generate a short, catchy title for a saved plan.
    - Occasion: {plan.occasion or "A special day"}
    - Restaurant: {plan.restaurant_name or "A great restaurant"}
    - Event: {plan.event_name or "An exciting event"}
    - Date: {plan.date.strftime('%A, %B %d')} if available.

    Example:
    - "Romantic Dinner & Live Jazz Night"
    - "Weekend Foodie Adventure"
    - "Exploring Chicago with a Twist"

    Now generate a unique title:
    """

    try:
        print("🔍 Sending prompt to ChatGPT AI...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.7,
        )

        title = response.choices[0].message.content.strip().replace('"', '').replace("'", "")

        print(f"✅ AI-Generated Title: {title}")  # Debug Statement

        # ✅ Save title to the database
        plan.title = title
        plan.save()

        return title

    except Exception as e:
        print(f"❌ AI Error: {e}")  # Debugging
        return "A Memorable Experience"
