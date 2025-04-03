from django.urls import path,  include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegistrationView, UserLoginView
from django.contrib import admin

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),  # User Registration API
    path('login/', UserLoginView.as_view(), name='login'),  # Custom login API
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
