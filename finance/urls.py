from django.urls import path,  include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegistrationView, UserLoginView, CategoryViewSet, TransactionViewSet, FinancialSummaryView, BudgetView, BudgetSummaryView
from django.contrib import admin


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction') 


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),  # User Registration API
    path('login/', UserLoginView.as_view(), name='login'),  # Custom login API
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("summary/", FinancialSummaryView.as_view(), name="financial-summary"),
    path('budget/', BudgetView.as_view(), name='budget'),
    path("budget-summary/<str:month>/", BudgetSummaryView.as_view(), name="budget_summary"),
    path('', include(router.urls)),
]
