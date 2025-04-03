from django.urls import path,  include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegistrationView
from django.contrib import admin

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),  # User Registration API
]
