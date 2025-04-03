from rest_framework.permissions import AllowAny
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserLoginSerializer, CategorySerializer, TransactionSerializer, BudgetSerializer
from .models import Category, Transaction, Budget  # Import the Category, Transaction, and Budget models
from django.db import models  # Import models for database operations
from datetime import datetime  # Import datetime for date and time operations

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
    
class BudgetView(generics.GenericAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the budget for the current month"""
        current_month = datetime.now().strftime("%Y-%m")
        budget = Budget.objects.filter(user=request.user, month=current_month).first()
        if not budget:
            return Response({"message": "No budget set for this month."}, status=status.HTTP_404_NOT_FOUND)

        # Calculate total expenses for the current month
        total_expenses = Transaction.objects.filter(
            user=request.user,
            transaction_type="expense",
            date__startswith=current_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        remaining_budget = float(budget.amount) - float(total_expenses)

        return Response({
            "budget": float(budget.amount),
            "expenses": float(total_expenses),
            "remaining": remaining_budget
        })

    def post(self, request):
        """Set a budget for the current month"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            month = serializer.validated_data['month']
            existing_budget = Budget.objects.filter(user=request.user, month=month).first()

            if existing_budget:
                return Response({"error": "Budget for this month already exists."}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


