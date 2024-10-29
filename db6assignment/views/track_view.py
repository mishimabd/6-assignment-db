import datetime
import json

from bson import ObjectId
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import redis

from db6assignment.views.product_view import products_collection

# Connect to the Redis server
redis_client = redis.Redis(host='localhost', port=6379, db=0)


@csrf_exempt
@require_http_methods(["POST"])
def save_product(request):
    try:
        body = json.loads(request.body)
        user_id = body.get("user_id")
        product_id = body.get("product_id")
        interaction_type = "save"

        # Validate required fields
        if not all([user_id, product_id, interaction_type]):
            return HttpResponse("User ID, Product ID, and interaction type are required", status=400)

        # Generate a Redis key for this user's interaction history
        redis_key = f"user:{user_id}:interactions"

        # Store the interaction in Redis
        redis_client.rpush(redis_key, json.dumps({
            "product_id": product_id,
            "interaction_type": interaction_type,
            "timestamp": str(datetime.datetime.now())
        }))

        return JsonResponse({"message": "User interaction recorded successfully"}, status=201)

    except (json.JSONDecodeError, KeyError):
        return HttpResponse("Invalid JSON", status=400)
    except Exception as e:
        return HttpResponse(f"Internal server error: {str(e)}", status=500)


@csrf_exempt
@require_http_methods(["POST"])
def like_product(request):
    try:
        # Parse the request body
        body = json.loads(request.body)
        user_id = body.get("user_id")
        product_id = body.get("product_id")
        interaction_type = "like"

        if not all([user_id, product_id, interaction_type]):
            return HttpResponse("User ID, Product ID, and interaction type are required", status=400)

        # Generate a Redis key for this user's interaction history
        redis_key = f"user:{user_id}:interactions"

        # Store the interaction in Redis
        redis_client.rpush(redis_key, json.dumps({
            "product_id": product_id,
            "interaction_type": interaction_type,
            "timestamp": str(datetime.datetime.now())
        }))

        return JsonResponse({"message": "User interaction recorded successfully"}, status=201)

    except (json.JSONDecodeError, KeyError):
        return HttpResponse("Invalid JSON", status=400)
    except Exception as e:
        return HttpResponse(f"Internal server error: {str(e)}", status=500)


@require_http_methods(["GET"])
def get_all_user_history(request):
    try:
        pattern = "user:*:interactions"
        keys = redis_client.keys(pattern)
        all_interaction_history = {}
        for key in keys:
            user_id = key.decode().split(":")[1]  # Extract user ID from the key
            interactions = redis_client.lrange(key, 0, -1)
            decoded_interactions = [json.loads(interaction) for interaction in interactions]

            # Store the interactions in the dictionary
            all_interaction_history[user_id] = decoded_interactions

        return JsonResponse({"history": all_interaction_history}, status=200)

    except Exception as e:
        return HttpResponse(f"Internal server error: {str(e)}", status=500)


@require_http_methods(["GET"])
def get_user_history(request):
    user_id = request.GET.get("user_id")

    # Validate that user_id is provided
    if not user_id:
        return HttpResponse("User ID is required", status=400)

    try:
        # Build the Redis key for the specific user
        redis_key = f"user:{user_id}:interactions"

        # Retrieve interactions for the user
        interactions = redis_client.lrange(redis_key, 0, -1)

        # Decode interactions and fetch product names
        decoded_interactions = []
        for interaction in interactions:
            interaction_data = json.loads(interaction)
            product_id = interaction_data.get("product_id")

            # Fetch the product name from MongoDB
            product = products_collection.find_one({"_id": ObjectId(product_id)}, {"name": 1})
            product_name = product["name"] if product else "Unknown Product"

            # Add the product name to the interaction data
            interaction_data["product_name"] = product_name
            decoded_interactions.append(interaction_data)

        # Return the interactions as a JSON response
        return JsonResponse({"user_id": user_id, "history": decoded_interactions}, status=200)

    except Exception as e:
        return HttpResponse(f"Internal server error: {str(e)}", status=500)
