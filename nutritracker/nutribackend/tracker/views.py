from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Meal, WaterIntake, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import os
import random
import re
from datetime import timedelta, date
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

try:
    import boto3
except ImportError:
    boto3 = None


def upload_image_to_s3(file_obj, filename):
    """
    Attempts AWS S3 upload if credentials exist in the system environment.
    Otherwise, falls back to local storage and returns a local server URL.
    """
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    if boto3 and bucket_name and aws_access_key and aws_secret_key:
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            # Include microseconds so uploaded filenames reflect the exact upload time
            s3_path = f"food_images/{timezone.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
            s3.upload_fileobj(file_obj, bucket_name, s3_path)
            region = os.environ.get('AWS_REGION', 'us-east-1')
            url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_path}"
            return url, True
        except Exception as e:
            print("S3 Upload failed, falling back to local storage:", e)
            
    # Local fallback
    # Include microseconds for precise timestamping in local filenames as well
    path = default_storage.save(f"food_images/{timezone.now().strftime('%Y%m%d%H%M%S%f')}_{filename}", ContentFile(file_obj.read()))
    return settings.MEDIA_URL + path, False


# Common food database for simulated recognition & voice parsing
FOOD_ITEMS_INFO = {
    'salad': {'name': 'Grilled Chicken Salad', 'cal': 350, 'prot': 25},
    'oatmeal': {'name': 'Oatmeal with Berries', 'cal': 250, 'prot': 6},
    'egg': {'name': 'Scrambled Eggs', 'cal': 180, 'prot': 12},
    'chicken': {'name': 'Grilled Chicken Breast', 'cal': 165, 'prot': 31},
    'pizza': {'name': 'Pizza Slice', 'cal': 285, 'prot': 12},
    'banana': {'name': 'Banana', 'cal': 105, 'prot': 1},
    'yogurt': {'name': 'Greek Yogurt & Nuts', 'cal': 200, 'prot': 15},
    'toast': {'name': 'Avocado Toast', 'cal': 280, 'prot': 7},
    'apple': {'name': 'Apple', 'cal': 95, 'prot': 0},
    'burger': {'name': 'Cheeseburger', 'cal': 400, 'prot': 20},
    'salmon': {'name': 'Grilled Salmon', 'cal': 350, 'prot': 34},
}


# ---------------- DASHBOARD ----------------
@api_view(['GET'])
def dashboard(request):
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
    
    jwt_auth = JWTAuthentication()
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "No token provided"}, status=401)
        
        token = auth_header.split(' ')[1]
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
    except (InvalidToken, AuthenticationFailed):
        return Response({"error": "Invalid token"}, status=401)

    today = timezone.now().date()
    meals = Meal.objects.filter(user=user, created_at__date=today)
    total_cal = sum([m.calories for m in meals])
    total_protein = sum([m.protein for m in meals])

    profile, _ = UserProfile.objects.get_or_create(user=user)
    water, _ = WaterIntake.objects.get_or_create(user=user, date=today)

    return Response({
        "calorie_goal": profile.calorie_goal,
        "total_calories": total_cal,
        "total_protein": total_protein,
        "calories_left": max(0, profile.calorie_goal - total_cal),
        "meals_count": meals.count(),
        "water": water.glasses,
        "bmi": profile.bmi()
    })


# ---------------- WATER ----------------
@api_view(['POST'])
def update_water(request):
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
    
    jwt_auth = JWTAuthentication()
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "No token provided"}, status=401)
        
        token = auth_header.split(' ')[1]
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
    except (InvalidToken, AuthenticationFailed):
        return Response({"error": "Invalid token"}, status=401)

    glasses = request.data.get('glasses')
    today = timezone.now().date()

    obj, _ = WaterIntake.objects.get_or_create(user=user, date=today)
    obj.glasses = glasses
    obj.save()

    return Response({"message": "Water updated", "glasses": obj.glasses})


# ---------------- SIGNUP ----------------
@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response({"error": "User already exists"}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    UserProfile.objects.create(user=user)

    return Response({"message": "User created"})


# ---------------- RESET PASSWORD (DEV ONLY) ----------------
@api_view(['POST'])
def reset_password(request):
    if not settings.DEBUG:
        return Response({"error": "Password reset endpoint is only available in DEBUG mode."}, status=403)

    identifier = (request.data.get('email') or request.data.get('username') or '').strip()
    new_password = (request.data.get('new_password') or '').strip()

    if not identifier or not new_password:
        return Response({"error": "Email/username and new_password are required."}, status=400)

    user = User.objects.filter(email__iexact=identifier).first()
    if user is None:
        user = User.objects.filter(username__iexact=identifier).first()

    if user is None:
        return Response({"error": "User not found."}, status=404)

    user.set_password(new_password)
    user.save()

    return Response({"message": f"Password reset successful for {user.username}."})


# ---------------- LOGIN ----------------
@api_view(['POST'])
def login_view(request):
    identifier = (request.data.get('username') or '').strip()
    password = (request.data.get('password') or '').strip()

    if not identifier or not password:
        return Response({"error": "Username/email and password are required."}, status=400)

    # Attempt direct authentication first.
    user = authenticate(username=identifier, password=password)

    # Try email login if identifier looks like an email.
    if user is None and '@' in identifier:
        email_user = User.objects.filter(email__iexact=identifier).first()
        if email_user:
            user = authenticate(username=email_user.username, password=password)

    # Try username case-insensitive match.
    if user is None:
        username_user = User.objects.filter(username__iexact=identifier).first()
        if username_user:
            user = authenticate(username=username_user.username, password=password)

    # Try removing spaces and matching username.
    if user is None and ' ' in identifier:
        compact_identifier = identifier.replace(' ', '')
        username_user = User.objects.filter(username__iexact=compact_identifier).first()
        if username_user:
            user = authenticate(username=username_user.username, password=password)

    # Additional fallback: substring match on username.
    if user is None:
        match_user = User.objects.filter(username__icontains=identifier).first()
        if match_user:
            user = authenticate(username=match_user.username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            "status": "success",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })

    return Response({"error": "Invalid username/email or password."}, status=401)


# ---------------- UPDATE PROFILE ----------------
@api_view(['POST'])
def update_profile(request):
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
    
    jwt_auth = JWTAuthentication()
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "No token provided"}, status=401)
        
        token = auth_header.split(' ')[1]
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
    except (InvalidToken, AuthenticationFailed):
        return Response({"error": "Invalid token"}, status=401)

    height = request.data.get('height')
    weight = request.data.get('weight')
    calorie_goal = request.data.get('calorie_goal')

    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    if height is not None:
        profile.height = float(height)
    if weight is not None:
        profile.weight = float(weight)
    if calorie_goal is not None:
        profile.calorie_goal = int(calorie_goal)
    
    profile.save()

    return Response({
        "message": "Profile updated",
        "bmi": profile.bmi(),
        "calorie_goal": profile.calorie_goal
    })


# ---------------- MEALS ----------------
@api_view(['GET'])
def get_meals(request):
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
    
    jwt_auth = JWTAuthentication()
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "No token provided"}, status=401)
        
        token = auth_header.split(' ')[1]
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
    except (InvalidToken, AuthenticationFailed):
        return Response({"error": "Invalid token"}, status=401)

    meals = Meal.objects.filter(user=user).order_by('-created_at')
    meal_data = []
    for meal in meals:
        meal_data.append({
            'id': meal.id,
            'name': meal.name,
            'calories': meal.calories,
            'protein': meal.protein,
            'type': meal.meal_type,
            'time': meal.meal_time,
            'date': meal.date.isoformat(),
            'image_url': meal.image_url,
            'created_at': meal.created_at.isoformat()
        })
    
    return Response(meal_data)


@api_view(['POST'])
def add_meal(request):
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
    
    jwt_auth = JWTAuthentication()
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "No token provided"}, status=401)
        
        token = auth_header.split(' ')[1]
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
    except (InvalidToken, AuthenticationFailed):
        return Response({"error": "Invalid token"}, status=401)

    name = request.data.get('name')
    calories = request.data.get('calories')
    protein = request.data.get('protein', 0)
    meal_type = request.data.get('meal_type', 'Meal')
    meal_time = request.data.get('meal_time', '')
    meal_date_input = request.data.get('date')

    if not name or calories is None:
        return Response({"error": "Name and calories are required"}, status=400)

    # Handle date - convert string to date object if needed
    if meal_date_input:
        from datetime import datetime
        try:
            meal_date = datetime.strptime(meal_date_input, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            meal_date = timezone.now().date()
    else:
        meal_date = timezone.now().date()

    # Normalize time format to HH:MM AM/PM
    if meal_time:
        import re
        # Try to parse various time formats
        time_match = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?', meal_time.strip())
        if time_match:
            hours = int(time_match.group(1))
            minutes = int(time_match.group(2))
            ampm = time_match.group(3)
            if ampm:
                # Already has AM/PM, just normalize format
                ampm = ampm.upper()
                # Ensure hours is in 1-12 range
                if hours == 0:
                    hours = 12
                elif hours > 12:
                    hours = hours - 12
            else:
                # No AM/PM, assume 24-hour format and convert
                ampm = 'AM' if hours < 12 else 'PM'
                hours = hours % 12
                hours = hours if hours else 12
            meal_time = f'{hours}:{minutes:02d} {ampm}'
        else:
            # If format doesn't match, use current time
            now = timezone.now()
            hours = now.hour
            minutes = now.minute
            ampm = 'AM' if hours < 12 else 'PM'
            hours = hours % 12
            hours = hours if hours else 12
            minutes = f'{minutes:02d}'
            meal_time = f'{hours}:{minutes} {ampm}'
    else:
        # If no time provided, set to current time
        now = timezone.now()
        hours = now.hour
        minutes = now.minute
        ampm = 'AM' if hours < 12 else 'PM'
        hours = hours % 12
        hours = hours if hours else 12
        minutes = f'{minutes:02d}'
        meal_time = f'{hours}:{minutes} {ampm}'

    image_url = request.data.get('image_url')
    meal = Meal.objects.create(
        user=user,
        name=name,
        calories=calories,
        protein=protein,
        meal_type=meal_type,
        meal_time=meal_time,
        date=meal_date,
        image_url=image_url
    )

    return Response({
        "message": "Meal added",
        "meal": {
            'id': meal.id,
            'name': meal.name,
            'calories': meal.calories,
            'protein': meal.protein,
            'type': meal.meal_type,
            'time': meal.meal_time,
            'date': meal.date.isoformat(),
            'image_url': meal.image_url,
            'created_at': meal.created_at.isoformat()
        }
    })


@api_view(['POST'])
def delete_meal(request):
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
    
    jwt_auth = JWTAuthentication()
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "No token provided"}, status=401)
        
        token = auth_header.split(' ')[1]
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
    except (InvalidToken, AuthenticationFailed):
        return Response({"error": "Invalid token"}, status=401)

    meal_id = request.data.get('meal_id')
    
    try:
        meal = Meal.objects.get(id=meal_id, user=user)
        meal.delete()
        return Response({"message": "Meal deleted"})
    except Meal.DoesNotExist:
        return Response({"error": "Meal not found"}, status=404)


# ---------------- IMAGE-BASED FOOD RECOGNITION ----------------
@api_view(['POST'])
def analyze_image(request):
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
    
    jwt_auth = JWTAuthentication()
    # For image analysis we allow anonymous requests from the static frontend
    # to simplify development (no user required). If an Authorization header
    # is present we'll try to validate it, otherwise proceed anonymously.
    user = None
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
    except Exception as e:
        # Don't block analysis for invalid tokens; just log and continue anonymously
        print('analyze_image: token validation failed:', e)
        
    image_file = request.FILES.get('image')
    if not image_file:
        # Also accept base64 data in JSON under 'image' for alternative clients
        b64 = request.data.get('image')
        if b64:
            return Response({"error": "Base64 image not supported in this demo"}, status=400)
        return Response({"error": "No image file provided"}, status=400)
    # Debug: print file info
    try:
        print('analyze_image: received file:', image_file.name, image_file.size)
    except Exception:
        pass
        
    # Cloud storage upload (simulated AWS S3)
    image_url, uploaded_to_s3 = upload_image_to_s3(image_file, image_file.name)
    
    # Classification heuristic based on filename
    fn = image_file.name.lower()
    matched_key = None
    for key in FOOD_ITEMS_INFO:
        if key in fn:
            matched_key = key
            break
            
    if matched_key:
        food = FOOD_ITEMS_INFO[matched_key]
        confidence = round(random.uniform(0.88, 0.98), 2)
    else:
        # Default or random food
        key = random.choice(list(FOOD_ITEMS_INFO.keys()))
        food = FOOD_ITEMS_INFO[key]
        confidence = round(random.uniform(0.60, 0.82), 2)
        
    return Response({
        "status": "success",
        "food_name": food['name'],
        "calories": food['cal'],
        "protein": food['prot'],
        "confidence": confidence,
        "image_url": image_url,
        "cloud_storage": "AWS S3 Bucket" if uploaded_to_s3 else "Local Server Media (Simulated S3)"
    })


# ---------------- VOICE-BASED FOOD LOGGING ----------------
@api_view(['POST'])
def parse_voice(request):
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
    
    jwt_auth = JWTAuthentication()
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "No token provided"}, status=401)
        
        token = auth_header.split(' ')[1]
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
    except (InvalidToken, AuthenticationFailed):
        return Response({"error": "Invalid token"}, status=401)
        
    text = request.data.get('text', '').lower().strip()
    if not text:
        return Response({"error": "No text content provided"}, status=400)
        
    # Heuristics for quantity
    number_map = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'a': 1, 'an': 1
    }
    
    quantity = 1
    digit_match = re.search(r'\b\d+\b', text)
    if digit_match:
        quantity = int(digit_match.group(0))
    else:
        for w in text.split():
            if w in number_map:
                quantity = number_map[w]
                break
                
    # Detect Meal Type
    meal_type = 'Meal'
    if 'breakfast' in text:
        meal_type = 'Breakfast'
    elif 'lunch' in text:
        meal_type = 'Lunch'
    elif 'dinner' in text:
        meal_type = 'Dinner'
    elif 'snack' in text:
        meal_type = 'Snack'
        
    # Find matching foods
    matched_foods = []
    sorted_keys = sorted(FOOD_ITEMS_INFO.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        if key in text:
            # Prevent double matching
            already_matched = False
            for mf in matched_foods:
                if key in mf['name'].lower():
                    already_matched = True
                    break
            if not already_matched:
                matched_foods.append({
                    'name': FOOD_ITEMS_INFO[key]['name'],
                    'cal': FOOD_ITEMS_INFO[key]['cal'],
                    'prot': FOOD_ITEMS_INFO[key]['prot']
                })
                text = text.replace(key, '')
                
    if not matched_foods:
        # Check if they said "ate X" or "had X"
        match = re.search(r'(?:ate|had|eating|log|having)\s+([a-zA-Z\s]+?)(?:\s+for|\s+at|\s+this|\.|$)', text)
        if match:
            food_name = match.group(1).strip()
            # Remove minor numbers/articles
            for word in ['a', 'an', 'some', 'the', 'my', 'one', 'two', 'three']:
                food_name = re.sub(rf'\b{word}\b', '', food_name).strip()
            if food_name:
                matched_foods.append({
                    'name': food_name.title(),
                    'cal': 250,
                    'prot': 8
                })
                
    if not matched_foods:
        matched_foods.append({
            'name': 'Logged Food Entry',
            'cal': 200,
            'prot': 5
        })
        
    # Save the parsed meals to database
    logged_meals = []
    for food in matched_foods:
        cals = food['cal'] * quantity
        prots = food['prot'] * quantity
        name = food['name']
        if quantity > 1:
            name = f"{quantity}x {name}"
            
        time_str = timezone.now().strftime('%I:%M %p')
        
        # Decide category if unspecified
        db_type = meal_type
        if db_type == 'Meal':
            name_l = name.lower()
            if 'egg' in name_l or 'oatmeal' in name_l or 'toast' in name_l:
                db_type = 'Breakfast'
            elif 'salad' in name_l or 'burger' in name_l or 'sandwich' in name_l:
                db_type = 'Lunch'
            elif 'salmon' in name_l or 'steak' in name_l or 'pizza' in name_l:
                db_type = 'Dinner'
            else:
                db_type = 'Snack'
                
        meal = Meal.objects.create(
            user=user,
            name=name,
            calories=cals,
            protein=prots,
            meal_type=db_type,
            meal_time=time_str
        )
        logged_meals.append({
            'id': meal.id,
            'name': meal.name,
            'calories': meal.calories,
            'protein': meal.protein,
            'type': meal.meal_type,
            'time': meal.meal_time
        })
        
    return Response({
        "status": "success",
        "meals_added": logged_meals
    })


# ---------------- ADVANCED DATA ANALYTICS ----------------
@api_view(['GET'])
def analytics(request):
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
    
    jwt_auth = JWTAuthentication()
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "No token provided"}, status=401)
        
        token = auth_header.split(' ')[1]
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
    except (InvalidToken, AuthenticationFailed):
        return Response({"error": "Invalid token"}, status=401)
        
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    today = timezone.now().date()
    days_list = []
    calories_data = []
    water_data = []
    
    total_weekly_calories = 0
    total_weekly_water = 0
    days_on_track = 0
    
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_str = d.strftime('%a')
        days_list.append(day_str)
        
        # Calories
        day_meals = Meal.objects.filter(user=user, created_at__date=d)
        day_cal = sum([m.calories for m in day_meals])
        calories_data.append(day_cal)
        total_weekly_calories += day_cal
        
        if day_cal > 0 and day_cal <= profile.calorie_goal:
            days_on_track += 1
            
        # Water: only use recorded WaterIntake entries; do NOT backfill or synthesize data
        try:
            water_rec = WaterIntake.objects.filter(user=user, date=d).first()
            if water_rec:
                water_val = water_rec.glasses
            else:
                water_val = 0
        except Exception:
            water_val = 0
        water_data.append(water_val)
        total_weekly_water += water_val
        
    avg_calories = round(total_weekly_calories / 7, 1)
    avg_water = round(total_weekly_water / 7, 1)
    
    # BMI trend: only return current BMI; no synthetic trend generation
    current_bmi = profile.bmi()
    bmi_trend_data = []
            
    return Response({
        "weekly_avg_calories": avg_calories,
        "weekly_avg_water": avg_water,
        "days_on_track": days_on_track,
        "current_bmi": current_bmi,
        "days": days_list,
        "calories_series": calories_data,
        "water_series": water_data,
        "bmi_series": bmi_trend_data,
        "bmi_labels": ['W1', 'W2', 'W3', 'W4', 'W5', 'W6']
    })


# ---------------- SIMPLE HEALTH ASSISTANT ----------------
@api_view(['POST'])
def assistant(request):
    """Rule-based health assistant for simple Q&A and guidance.

    Accepts JSON: {"message": "..."}
    Returns: {"reply": "..."}
    """
    text = (request.data.get('message') or '').lower().strip()
    if not text:
        return Response({"reply": "Hi — tell me what you'd like help with (nutrition, calories, BMI, water, or meal logging)."})

    user = None
    profile = None
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
    jwt_auth = JWTAuthentication()
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            profile, _ = UserProfile.objects.get_or_create(user=user)
    except (InvalidToken, AuthenticationFailed, Exception):
        profile = None

    # session-backed mock profile for unauthenticated users
    mock = request.session.get('mock_profile', {}) if hasattr(request, 'session') else {}

    def find_food():
        keys = sorted(FOOD_ITEMS_INFO.keys(), key=len, reverse=True)
        for key in keys:
            if key in text:
                return key
        return None

    # parse natural language mock profile updates (e.g. 'my weight is 70 kg', 'height 175 cm')
    def parse_and_store_mock():
        changed = False
        # weight in kg or lb
        m = re.search(r"(weight|weigh)\s*(is|:|=)?\s*(\d+(?:\.\d+)?)\s*(kg|kgs|kilograms|lb|lbs|pounds)?", text)
        if m:
            val = float(m.group(3))
            unit = (m.group(4) or '').lower()
            if 'lb' in unit or 'pound' in unit:
                val = round(val * 0.453592, 1)
            mock['weight'] = val
            changed = True

        # height in cm or m
        m2 = re.search(r"(height)\s*(is|:|=)?\s*(\d+(?:\.\d+)?)\s*(cm|cm\.|m|meters|metres)?", text)
        if m2:
            val = float(m2.group(3))
            unit = (m2.group(4) or '').lower()
            if unit.startswith('m'):
                # meters to cm
                val = round(val * 100)
            mock['height_cm'] = val
            changed = True

        # age
        m3 = re.search(r"(age)\s*(is|:|=)?\s*(\d{1,3})", text)
        if m3:
            mock['age'] = int(m3.group(3))
            changed = True

        if changed and hasattr(request, 'session'):
            request.session['mock_profile'] = mock
        return changed

    # If user provided mock details in this message, parse and acknowledge
    if parse_and_store_mock():
        reply_parts = []
        if 'weight' in mock:
            reply_parts.append(f"Got it — recorded mock weight: {mock['weight']} kg.")
        if 'height_cm' in mock:
            reply_parts.append(f"Recorded mock height: {mock['height_cm']} cm.")
        if 'age' in mock:
            reply_parts.append(f"Recorded mock age: {mock['age']} years.")
        return Response({"reply": ' '.join(reply_parts)})

    def format_food_response(key):
        info = FOOD_ITEMS_INFO[key]
        return f"{info['name']} typically contains about {info['cal']} kcal and {info['prot']} g of protein per serving."

    def user_calorie_goal_response():
        # Prefer real profile, fall back to mock profile
        if profile and profile.calorie_goal:
            return f"Your daily calorie goal is {profile.calorie_goal} kcal. Use the dashboard to track intake and remaining calories."
        if mock.get('weight'):
            # rough estimate using weight * 30 kcal/kg
            est = int(mock['weight'] * 30)
            return f"Based on the mock weight you provided, a rough daily calorie estimate is {est} kcal. Personal needs vary; consider activity level."
        return "A common daily calorie target is about 2000 kcal for many adults, but personal needs vary by age, sex, and activity."

    def user_protein_goal_response():
        if profile and profile.weight:
            target = round(profile.weight * 0.8)
            return f"A typical protein guideline is about 0.8 g per kg of body weight, so around {target} g per day for your weight."
        if mock.get('weight'):
            target = round(mock['weight'] * 0.8)
            return f"Based on your mock weight, a guideline is about {target} g protein per day."
        return "A healthy protein goal is generally 0.8 grams per kilogram of body weight. If you know your weight, multiply it by 0.8 to estimate daily protein needs."

    def user_bmi_response():
        # Prefer real profile, else mock values
        if profile and profile.height and profile.weight:
            return f"Your BMI is {profile.bmi():.1f}. BMI categories: under 18.5 is underweight, 18.5–24.9 is normal, 25–29.9 is overweight, 30+ is obese."
        if mock.get('weight') and mock.get('height_cm'):
            h_m = mock['height_cm'] / 100.0
            bmi_val = mock['weight'] / (h_m * h_m)
            return f"Based on mock details, your BMI is {bmi_val:.1f}. BMI categories: under 18.5 underweight, 18.5–24.9 normal, 25–29.9 overweight, 30+ obese."
        return "If you enter your height and weight in Profile, I can calculate BMI for you. You can also tell me e.g. 'weight 70 kg' and 'height 175 cm' to use mock data."

    def water_advice_response():
        if profile:
            return "Aim for about 6-8 glasses of water daily. Track your intake in the Water page to see how close you are to your goal."
        return "A general recommendation is 6-8 glasses of water per day, but your needs depend on your activity level and climate."

    # User intent matching
    if any(w in text for w in ['hi', 'hello', 'hey', 'good morning', 'good evening']):
        return Response({"reply": "Hello! I can help with calories, protein, water, BMI, and meal logging. Ask me a question like 'How many calories in pizza?' or 'What is my BMI?'."})

    food_key = find_food()
    if 'calorie' in text or 'calories' in text:
        if food_key:
            return Response({"reply": format_food_response(food_key)})
        if 'goal' in text or 'eat per day' in text or 'daily intake' in text:
            return Response({"reply": user_calorie_goal_response()})
        return Response({"reply": "Tell me which food item, or ask 'How many calories should I eat per day?'."})

    if 'protein' in text:
        if food_key:
            info = FOOD_ITEMS_INFO[food_key]
            return Response({"reply": f"{info['name']} contains about {info['prot']} g of protein per serving and {info['cal']} kcal."})
        if 'need' in text or 'per day' in text or 'daily' in text:
            return Response({"reply": user_protein_goal_response()})
        return Response({"reply": "Ask me 'How much protein is in banana?' or 'How much protein should I eat per day?'."})

    if 'water' in text or 'glasses' in text or 'hydrate' in text:
        if 'how much' in text or 'recommend' in text or 'need' in text:
            return Response({"reply": water_advice_response()})
        if user:
            today = timezone.now().date()
            water_today = WaterIntake.objects.filter(user=user, date=today).first()
            if water_today:
                return Response({"reply": f"You have logged {water_today.glasses} glasses of water today. Keep going if you want to reach your goal."})
        if mock.get('water'):
            return Response({"reply": f"Mock water logged: {mock['water']} glasses today."})
        return Response({"reply": "Track your water on the Water page and I can give you a daily summary. You can also tell me e.g. 'I drank 3 glasses' and I'll remember it for this session."})

    if 'bmi' in text:
        if 'what is' in text or 'calculate' in text or 'my bmi' in text:
            return Response({"reply": user_bmi_response()})
        return Response({"reply": "BMI is a simple ratio of weight to height. Ask 'What is my BMI?' after entering your height and weight in profile."})

    if any(w in text for w in ['log', 'add', 'i had', 'i ate', 'ate', 'had']) and food_key:
        info = FOOD_ITEMS_INFO[food_key]
        # Optionally persist as a mock meal if session-only
        if any(w in text for w in ['log', 'add', 'i had', 'i ate', 'ate', 'had']):
            # If authenticated, create a Meal record
            try:
                if user:
                    m = Meal.objects.create(user=user, name=info['name'], calories=info['cal'], protein=info['prot'])
                    return Response({"reply": f"Logged {info['name']} ({info['cal']} kcal, {info['prot']} g protein) to your account."})
                else:
                    # session mock log
                    mock_meals = request.session.get('mock_meals', [])
                    mock_meals.insert(0, { 'name': info['name'], 'cal': info['cal'], 'prot': info['prot'], 'created_at': timezone.now().isoformat() })
                    request.session['mock_meals'] = mock_meals
                    return Response({"reply": f"Mock-logged {info['name']} for this session: {info['cal']} kcal, {info['prot']} g protein."})
            except Exception:
                pass
        return Response({"reply": f"I detected {info['name']} in your message. It is about {info['cal']} kcal and {info['prot']} g protein. Use the Add Meal screen to log it, or tell me 'log {info['name']}'."})

    if any(w in text for w in ['help', 'tips', 'advice']):
        return Response({"reply": "I can help with nutrition advice, calories, protein, BMI, water intake, weight management, healthy foods, meal planning, and much more. Try asking about any nutrition topic!"})

    # Extended knowledge base for general nutrition questions
    NUTRITION_KNOWLEDGE = {
        'healthy foods': "Healthy foods include fruits, vegetables, whole grains, lean proteins, nuts, and seeds. Focus on colorful fruits and veggies, whole grains like oats and brown rice, and lean proteins like chicken, fish, and legumes.",
        'weight loss': "For weight loss, create a calorie deficit by eating fewer calories than you burn. Aim for 0.5-1 kg weight loss per week. Combine diet with regular exercise. Focus on protein-rich foods, fiber, and avoid processed foods and sugary drinks.",
        'weight gain': "For healthy weight gain, eat a calorie surplus with nutrient-dense foods. Include more protein, healthy fats (avocados, nuts, olive oil), and complex carbohydrates. Strength training can help build muscle mass.",
        'carbs': "Carbohydrates are your body's main energy source. Choose complex carbs like whole grains, fruits, and vegetables over simple carbs like sugar and white bread. Most adults need 45-65% of daily calories from carbs.",
        'fats': "Healthy fats are essential for hormone production and nutrient absorption. Include avocados, nuts, seeds, olive oil, and fatty fish. Limit saturated fats and avoid trans fats. Aim for 20-35% of daily calories from fat.",
        'vitamins': "Key vitamins include Vitamin A (vision, immune), Vitamin C (immune, collagen), Vitamin D (bones), Vitamin E (antioxidant), and B vitamins (energy). Eat a variety of colorful fruits and vegetables to get all essential vitamins.",
        'minerals': "Important minerals include calcium (bones), iron (blood), potassium (heart), magnesium (muscles), and zinc (immune). Dairy, leafy greens, nuts, seeds, and whole grains are good sources.",
        'fiber': "Fiber aids digestion and helps maintain healthy cholesterol levels. Adults need 25-30g daily. Good sources include whole grains, fruits, vegetables, legumes, nuts, and seeds.",
        'sugar': "Limit added sugars to less than 10% of daily calories (about 50g for a 2000 kcal diet). Excess sugar can lead to weight gain, diabetes, and heart disease. Choose natural sugars from fruits instead.",
        'salt': "Limit sodium to less than 2300mg per day (about 1 teaspoon). Excess salt can increase blood pressure. Use herbs and spices for flavor instead of salt.",
        'breakfast': "A healthy breakfast should include protein, fiber, and healthy fats. Examples: oatmeal with berries and nuts, Greek yogurt with fruit, eggs with whole grain toast, or a smoothie with protein powder.",
        'snacks': "Healthy snack options include fruits, nuts, yogurt, hummus with vegetables, or a small portion of whole grain crackers with cheese. Keep snacks under 200 calories.",
        'exercise': "Aim for at least 150 minutes of moderate exercise or 75 minutes of vigorous exercise per week. Include strength training 2-3 times per week. Exercise helps maintain a healthy weight and reduces disease risk.",
        'metabolism': "Metabolism is the process by which your body converts food into energy. Factors affecting metabolism include age, muscle mass, activity level, and genetics. Building muscle through strength training can boost metabolism.",
        'diet': "A balanced diet includes a variety of foods from all food groups. Focus on whole, unprocessed foods. Include plenty of fruits and vegetables, lean proteins, whole grains, and healthy fats.",
        'supplements': "Most people can get all necessary nutrients from a balanced diet. Supplements may be needed for specific deficiencies (like Vitamin D or iron). Consult a healthcare provider before starting any supplements.",
        'diabetes': "For diabetes management, focus on controlling blood sugar through diet. Choose complex carbs with low glycemic index, monitor portion sizes, eat regular meals, and limit sugary foods and drinks.",
        'heart health': "For heart health, limit saturated fats, trans fats, and sodium. Eat more fruits, vegetables, whole grains, and fatty fish rich in omega-3s. Maintain a healthy weight and exercise regularly.",
        'digestion': "For healthy digestion, eat plenty of fiber, stay hydrated, and include probiotics like yogurt. Eat slowly and chew thoroughly. Regular exercise also helps digestion.",
        'energy': "To maintain energy levels, eat regular meals with complex carbs and protein. Stay hydrated, get enough sleep, and include iron-rich foods if you feel fatigued. Avoid large meals that can cause energy crashes.",
        'muscle building': "For muscle building, consume adequate protein (1.2-2.0g per kg body weight), eat enough calories to support growth, include complex carbs for energy, and time protein intake around workouts.",
        'vegetarian': "A vegetarian diet can be healthy with proper planning. Ensure adequate protein from legumes, tofu, tempeh, nuts, and seeds. Include iron-rich foods with vitamin C for absorption, and consider B12 supplements.",
        'vegan': "A vegan diet requires careful planning for protein, B12, iron, calcium, and omega-3s. Include legumes, nuts, seeds, fortified foods, and consider supplements for B12 and possibly omega-3s.",
        'gluten free': "A gluten-free diet is necessary for celiac disease or gluten sensitivity. Focus on naturally gluten-free foods: fruits, vegetables, meat, fish, dairy, nuts, and gluten-free grains like rice, quinoa, and buckwheat.",
        'keto': "The ketogenic diet is very low-carb, high-fat. It can help with weight loss but may not be sustainable long-term. Consult a healthcare provider before starting, as it may not be suitable for everyone.",
        'intermittent fasting': "Intermittent fasting involves cycling between eating and fasting periods. Common methods include 16:8 (16 hours fasting, 8 hours eating). It may help with weight loss but should be done under guidance.",
        'alcohol': "Moderate alcohol intake is up to 1 drink per day for women, 2 for men. Excess alcohol can lead to weight gain, liver damage, and increased disease risk. If you drink, do so in moderation.",
        'caffeine': "Moderate caffeine intake (up to 400mg daily) is safe for most adults. Too much can cause anxiety, insomnia, and digestive issues. Be mindful of caffeine in coffee, tea, energy drinks, and soda.",
        'sleep': "Aim for 7-9 hours of quality sleep per night. Poor sleep can affect hunger hormones, leading to increased appetite and weight gain. Maintain a consistent sleep schedule and avoid screens before bed.",
        'stress': "Chronic stress can lead to overeating and weight gain. Manage stress through exercise, meditation, deep breathing, or hobbies. Stress management is important for overall health.",
        'meal prep': "Meal prep involves preparing meals in advance. It saves time, ensures healthy options are available, and helps with portion control. Start with prepping 2-3 days worth of meals.",
        'eating out': "When eating out, look for grilled, baked, or steamed options. Ask for dressings and sauces on the side. Choose water or unsweetened drinks instead of soda. Be mindful of portion sizes.",
        'organic': "Organic foods are grown without synthetic pesticides or fertilizers. They may reduce exposure to chemicals but aren't necessarily more nutritious. Choose organic when possible, especially for the 'Dirty Dozen' produce.",
        'processed foods': "Limit processed foods as they often contain added sugars, sodium, and unhealthy fats. Focus on whole, unprocessed foods. If buying processed foods, read labels and choose options with simple ingredients.",
        'sugar substitutes': "Sugar substitutes can help reduce calorie intake but should be used in moderation. Some people may experience digestive issues. Natural alternatives like stevia or monk fruit may be preferable to artificial sweeteners.",
        'dairy': "Dairy provides calcium, protein, and vitamin D. Choose low-fat options when possible. If lactose intolerant, consider lactose-free dairy or alternatives like fortified plant milks.",
        'eggs': "Eggs are a complete protein source with essential nutrients. Most people can eat 1-2 eggs daily as part of a healthy diet. Those with high cholesterol should consult their doctor about egg intake.",
        'fish': "Fatty fish like salmon, mackerel, and sardines are rich in omega-3 fatty acids, which support heart and brain health. Aim for 2-3 servings of fish per week. Be mindful of mercury in certain fish.",
        'nuts': "Nuts are healthy sources of protein, healthy fats, fiber, and antioxidants. A small handful (about 1 oz) daily is beneficial. Choose unsalted varieties when possible.",
        'seeds': "Seeds like chia, flax, pumpkin, and sunflower are nutrient-dense with healthy fats, protein, and minerals. Add them to smoothies, yogurt, or salads for extra nutrition.",
        'legumes': "Legumes (beans, lentils, chickpeas) are excellent plant-based protein sources rich in fiber and minerals. They support heart health and help maintain stable blood sugar levels.",
        'whole grains': "Whole grains like oats, quinoa, brown rice, and whole wheat provide fiber, B vitamins, and minerals. They support digestive health and help maintain steady energy levels.",
        'fruits': "Fruits are rich in vitamins, minerals, fiber, and antioxidants. Aim for 2-3 servings daily. Whole fruits are preferable to fruit juice, which lacks fiber and can be high in sugar.",
        'vegetables': "Vegetables are low in calories but high in nutrients. Aim for 3-5 servings daily. Include a variety of colors to get different nutrients. Both raw and cooked vegetables are healthy.",
        'antioxidants': "Antioxidants protect cells from damage. Found in colorful fruits and vegetables, nuts, seeds, and dark chocolate. A diet rich in antioxidants may reduce disease risk.",
        'inflammation': "Anti-inflammatory foods include fatty fish, berries, leafy greens, nuts, olive oil, and tomatoes. Limit processed foods, sugar, and refined carbs to reduce inflammation.",
        'gut health': "Support gut health with probiotics (yogurt, kefir, fermented foods) and prebiotics (fiber-rich foods). A healthy gut microbiome supports digestion, immunity, and mental health.",
        'food allergies': "Common food allergies include peanuts, tree nuts, dairy, eggs, soy, wheat, fish, and shellfish. If you suspect a food allergy, see a healthcare provider for proper diagnosis.",
        'food intolerance': "Food intolerances (like lactose intolerance) cause digestive issues. Unlike allergies, they don't involve the immune system. Identify trigger foods and avoid them or find alternatives.",
        'pregnancy': "During pregnancy, increase intake of folate, iron, calcium, and protein. Avoid raw fish, unpasteurized dairy, excessive caffeine, and alcohol. Consult a healthcare provider for personalized nutrition advice.",
        'kids nutrition': "Children need balanced nutrition for growth. Include plenty of fruits, vegetables, whole grains, and lean proteins. Limit sugary drinks and snacks. Establish healthy eating habits early.",
        'seniors nutrition': "Older adults may need fewer calories but still require adequate nutrients. Focus on protein, calcium, vitamin D, and B12. Stay hydrated and eat nutrient-dense foods.",
        'budget healthy eating': "Eat healthy on a budget by buying seasonal produce, choosing frozen vegetables, buying in bulk, cooking at home, and reducing meat consumption. Plan meals to reduce waste.",
        'reading labels': "Read food labels to check serving sizes, calories, nutrients, and ingredients. Look for short ingredient lists with recognizable words. Be aware of hidden sugars and sodium.",
        'portion control': "Use smaller plates, measure portions, and be mindful of serving sizes. Restaurant portions are often much larger than needed. Listen to hunger and fullness cues.",
        'mindful eating': "Mindful eating involves paying attention to hunger cues, eating slowly, and savoring food. It can help prevent overeating and improve relationship with food. Avoid distractions while eating.",
    }

    # Check extended knowledge base
    for key, value in NUTRITION_KNOWLEDGE.items():
        if key in text or text in key:
            return Response({"reply": value})

    # General nutrition questions
    if any(w in text for w in ['what should i eat', 'healthy diet', 'balanced diet', 'good food']):
        return Response({"reply": "A healthy diet includes a variety of whole foods: plenty of fruits and vegetables, whole grains, lean proteins, healthy fats, and limited processed foods. Focus on nutrient density and balance across all food groups."})

    if any(w in text for w in ['lose weight', 'weight loss', 'dieting', 'burn fat']):
        return Response({"reply": NUTRITION_KNOWLEDGE['weight loss']})

    if any(w in text for w in ['gain weight', 'build muscle', 'bulk up']):
        return Response({"reply": NUTRITION_KNOWLEDGE['weight gain']})

    if any(w in text for w in ['carbohydrate', 'carbs', 'low carb']):
        return Response({"reply": NUTRITION_KNOWLEDGE['carbs']})

    if any(w in text for w in ['fat', 'fats', 'healthy fat']):
        return Response({"reply": NUTRITION_KNOWLEDGE['fats']})

    if any(w in text for w in ['vitamin', 'vitamins']):
        return Response({"reply": NUTRITION_KNOWLEDGE['vitamins']})

    if any(w in text for w in ['mineral', 'minerals']):
        return Response({"reply": NUTRITION_KNOWLEDGE['minerals']})

    if any(w in text for w in ['fiber', 'digestive']):
        return Response({"reply": NUTRITION_KNOWLEDGE['fiber']})

    if any(w in text for w in ['sugar', 'sweet', 'candy']):
        return Response({"reply": NUTRITION_KNOWLEDGE['sugar']})

    if any(w in text for w in ['salt', 'sodium']):
        return Response({"reply": NUTRITION_KNOWLEDGE['salt']})

    if any(w in text for w in ['breakfast', 'morning meal']):
        return Response({"reply": NUTRITION_KNOWLEDGE['breakfast']})

    if any(w in text for w in ['snack', 'snacking']):
        return Response({"reply": NUTRITION_KNOWLEDGE['snacks']})

    if any(w in text for w in ['exercise', 'workout', 'fitness', 'training']):
        return Response({"reply": NUTRITION_KNOWLEDGE['exercise']})

    if any(w in text for w in ['metabolism', 'metabolic']):
        return Response({"reply": NUTRITION_KNOWLEDGE['metabolism']})

    if any(w in text for w in ['supplement', 'vitamin pill']):
        return Response({"reply": NUTRITION_KNOWLEDGE['supplements']})

    # Fallback: attempt to answer short factual questions about foods
    if '?' in text or text.split()[:3]:
        # If contains a food word, respond with food info
        if food_key:
            return Response({"reply": format_food_response(food_key)})
        # If asks about BMI or protein but not caught above, suggest next steps
        if any(k in text for k in ['how', 'what', 'why', 'when', 'where', 'which']):
            return Response({"reply": "I can help with nutrition calculations, food calories, BMI, and logging. Try asking 'How many calories in an apple?' or provide mock details like 'weight 70 kg' for personalized answers."})

    return Response({"reply": "I'm still learning! Try asking me about calories, protein, BMI, water intake, healthy foods, weight management, specific nutrients, or meal logging. You can also provide mock details like 'weight 70 kg' and 'height 175 cm' for personalized answers."})
