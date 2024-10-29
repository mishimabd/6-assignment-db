from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["mongo"]
products_collection = db["products"]


@require_http_methods(["GET"])
def view_catalog(request):
    try:
        # Fetch all products and convert `_id` to string
        products = []
        for product in products_collection.find({}):
            product['_id'] = str(product['_id'])  # Convert ObjectId to string
            products.append(product)

        return JsonResponse({"products": products}, status=200)

    except Exception as e:
        return HttpResponse(f"Internal server error: {str(e)}", status=500)
