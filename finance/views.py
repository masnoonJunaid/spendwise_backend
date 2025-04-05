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
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from spend_wise.utils.authentication import JWTAuthenticationFromCookie



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

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = Response({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }, status=status.HTTP_200_OK)

            # Set cookies
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,  # Set to False for local dev, True for production
                samesite='Lax',
                max_age=3600  # 1 hour
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=7 * 24 * 3600  # 7 days
            )

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [JWTAuthenticationFromCookie]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"message": "Logout successful"}, status=200)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    

    
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
    

class BudgetSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, month):
        user = request.user
        try:
            # Parse month from URL (expected format: YYYY-MM)
            year, month = map(int, month.split('-'))
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

            # Get user's budget for the given month
            budget_obj = Budget.objects.filter(user=user, month=start_date.date()).first()
            budget_amount = budget_obj.amount if budget_obj else 0  # Default to 0 if no budget set

            # Calculate total expenses for the month
            total_expenses = Transaction.objects.filter(
                user=user, 
                transaction_type="expense", 
                date__gte=start_date, 
                date__lt=end_date
            ).aggregate(total=models.Sum('amount'))['total'] or 0  # Default to 0

            # Calculate remaining budget
            remaining_budget = budget_amount - total_expenses
            over_budget = total_expenses > budget_amount

            # Response data
            data = {
                "month": f"{year}-{month:02d}",
                "budget": budget_amount,
                "total_expenses": total_expenses,
                "remaining_budget": remaining_budget,
                "over_budget": over_budget
            }
            return Response(data, status=200)

        except ValueError:
            return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)
