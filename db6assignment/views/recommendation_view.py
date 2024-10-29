from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from bson import ObjectId
import json
import random

from db6assignment.views.product_view import products_collection
from db6assignment.views.track_view import redis_client


@require_http_methods(["GET"])
def recommend_product(request):
    user_id = request.GET.get("user_id")
    try:
        if not user_id:
            return HttpResponse("User ID is required", status=400)

        # Build the Redis key for the specific user
        redis_key = f"user:{user_id}:interactions"
        interactions = redis_client.lrange(redis_key, 0, -1)
        decoded_interactions = [json.loads(interaction) for interaction in interactions]

        # Extract product IDs and gather product categories from user interactions
        interacted_product_ids = {interaction["product_id"] for interaction in decoded_interactions}
        interacted_categories = set()

        for product_id in interacted_product_ids:
            product = products_collection.find_one({"_id": ObjectId(product_id)})
            if product and "category" in product:
                interacted_categories.add(product["category"])

        # Fetch new products in these categories that the user hasn't interacted with yet
        recommendations = list(products_collection.find({
            "category": {"$in": list(interacted_categories)},
            "_id": {"$nin": [ObjectId(pid) for pid in interacted_product_ids]}
        }, {"_id": 1, "name": 1, "category": 1, "description": 1}))

        # Convert ObjectId to string for JSON serialization
        for recommendation in recommendations:
            recommendation["_id"] = str(recommendation["_id"])

        # If there are too many recommendations, we can randomly select a few
        recommended_products = random.sample(recommendations, min(len(recommendations), 5))

        return JsonResponse({"user_id": user_id, "recommended_products": recommended_products}, status=200)

    except Exception as e:
        return HttpResponse(f"Internal server error: {str(e)}", status=500)
