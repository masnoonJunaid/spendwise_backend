from rest_framework.permissions import AllowAny
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserLoginSerializer, CategorySerializer, TransactionSerializer
from .models import Category, Transaction  # Import the Category and Transaction models
from django.db import models  # Import models for database operations

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Allowing anyone to register (no token required)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generating JWT token after successful registration, this token sent in response, this can be updated for 2factor authentication or other verufication methods
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "refresh": str(refresh),  # Refresh token
                "access": str(refresh.access_token),  # Access token
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]  # Get authenticated user

            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can access

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)  #Users can only see their own categories

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  #Save category with the logged-in user
        

class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can use this

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)  # Filter transactions for logged-in user

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Assign transaction to logged-in user


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can use it

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)  # Only fetch user's transactions

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Auto-assign user when creating a transaction

class FinancialSummaryView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can access

    def get(self, request):
        user = request.user  # Get the logged-in user

        # Calculate total income and expenses
        total_income = Transaction.objects.filter(user=user, transaction_type="income").aggregate(total=models.Sum("amount"))["total"] or 0
        total_expense = Transaction.objects.filter(user=user, transaction_type="expense").aggregate(total=models.Sum("amount"))["total"] or 0

        balance = total_income - total_expense  # Remaining balance

        return Response({
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance
        })