import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.
class UserProfile(models.Model):
    """Stores additional user settings like preferred currency."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    currency = models.CharField(max_length=10, default="USD")
    default_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Profile of {self.user.username}"
    
class Category(models.Model):
    CATEGORY_TYPES = (
        ("income", "Income"),
        ("expense", "Expense"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Each user has their own categories
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)  # "income" or "expense"

    def __str__(self):
        return self.name