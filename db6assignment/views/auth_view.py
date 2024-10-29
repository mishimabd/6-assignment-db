import datetime
import uuid
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pymongo import MongoClient
import json
import bcrypt
import jwt

# Initialize MongoDB client
client = MongoClient("mongodb://localhost:27017/")
db = client["mongo"]
users_collection = db["users"]
SECRET_KEY = "secret_key_mishima"
ALGORITHM = "HS256"

@require_http_methods(["POST"])
@csrf_exempt
def login(request):
    try:
        # Parse the request body
        body = json.loads(request.body)
        login_req = body.get("login")
        password_req = body.get("password")
    except (json.JSONDecodeError, KeyError):
        return HttpResponse("Invalid JSON", status=400)

    # Fetch the user record based on login from MongoDB
    user = users_collection.find_one({"username": login_req}, {"uuid": 1, "password": 1})

    if user is None:
        return HttpResponse("Invalid login or password", status=401)

    # Extract user_id (UUID) and password hash
    user_id = user["uuid"]
    hashed_password = user["password"]

    # Validate password
    if not bcrypt.checkpw(password_req.encode(), hashed_password.encode()):
        return HttpResponse("Invalid login or password", status=401)

    try:
        # Generate token
        token = generate_token(str(user_id))
    except Exception as e:
        return HttpResponse(f"Internal server error: {str(e)}", status=500)

    # Return token as JSON response
    return JsonResponse({"token": token})


def generate_token(user_id):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    payload = {
        "user_id": user_id,
        "exp": expiration_time,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


@require_http_methods(["POST"])
@csrf_exempt
def signup(request):
    try:
        # Parse request body
        body = json.loads(request.body)
        username = body.get("username")
        password = body.get("password")
        name = body.get("name")
        age = body.get("age")

        # Check if all required fields are provided
        if not username or not password:
            return HttpResponse("Username and password are required", status=400)

        # Check if username already exists
        if users_collection.find_one({"username": username}):
            return HttpResponse("Username already exists", status=400)

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Generate unique user ID (UUID)
        user_id = str(uuid.uuid4())

        # Create the user document
        user_data = {
            "uuid": user_id,
            "username": username,
            "password": hashed_password,
            "name": name,
            "age": age
            # Add other profile fields as needed
        }

        # Insert user data into MongoDB
        users_collection.insert_one(user_data)

        # Respond with success and user_id
        return JsonResponse({"message": "User created successfully", "user_id": user_id}, status=201)

    except (json.JSONDecodeError, KeyError):
        return HttpResponse("Invalid JSON", status=400)
    except Exception as e:
        return HttpResponse(f"Internal server error: {str(e)}", status=500)