from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager

# Create your models here.

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, blank=False, null=False, verbose_name='Email',default='testing_email')
    USERNAME_FIELD = 'email'
    first_name = models.CharField(max_length=100, verbose_name='First Name', blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name='Last Name', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance_sheet = models.FileField(upload_to='balance_sheets/', null=True, blank=True)
    objects = UserManager()
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    splitting_method = models.CharField(max_length=10, choices=[
        ('equal', 'Equal'),
        ('exact', 'Exact'),
        ('percentage', 'Percentage')
    ])
    is_settled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title + ' - ' + str(self.amount)
    
class Participant(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    split_amount = models.DecimalField(max_digits=10, decimal_places=2)

    is_settled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.expense.title + ' - ' + self.user.email + ' - ' + str(self.split_amount)