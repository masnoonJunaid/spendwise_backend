from django.urls import path,  include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegistrationView, UserLoginView, CategoryViewSet
from django.contrib import admin


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),  # User Registration API
    path('login/', UserLoginView.as_view(), name='login'),  # Custom login API
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
