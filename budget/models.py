from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    """
    Represents a user-created transaction category.

    Categories are used to organise financial records and are
    classified as either income or expense.
    """

    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """
    Represents a financial transaction created by a user.

    Each transaction belongs to one user and one category,
    and stores the amount, date, and optional description.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - €{self.amount}"


class Profile(models.Model):
    """
    Store premium membership status for users.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    is_premium = models.BooleanField(default=False)

def __str__(self):
        return self.user.username
  
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create profile for new users.
    """
    if created:
        Profile.objects.create(user=instance)