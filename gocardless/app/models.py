from django.contrib.auth.models import AbstractUser
from django.db import models

class Person(AbstractUser):
    age = models.PositiveIntegerField(blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True)
    image = models.ImageField(upload_to='user_profile/', blank=True)
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions')

    def __str__(self):
        return self.username
    
class BankDetails(models.Model):
    user = models.OneToOneField(Person, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    routing_number = models.CharField(max_length=20)
    current_balance = models.FloatField(default=100)
    # Add more fields as needed

    def __str__(self):
        return f"Bank details for {self.user.username}"
