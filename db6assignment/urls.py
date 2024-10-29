"""
URL configuration for db6assignment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from db6assignment.views.auth_view import login, signup
from db6assignment.views.product_view import view_catalog
from db6assignment.views.recommendation_view import recommend_product
from db6assignment.views.track_view import get_all_user_history, like_product, save_product, get_user_history

urlpatterns = [
    path('auth/login', login),
    path('auth/signup', signup),
    path('products/view', view_catalog),
    path('products/like', like_product),
    path('products/save', save_product),
    path('track/history', get_all_user_history),
    path('track/user', get_user_history),
    path('recommendations', recommend_product),
    path('admin', admin.site.urls),
]
