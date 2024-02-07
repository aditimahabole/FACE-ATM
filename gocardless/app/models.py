from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
import re

class Person(AbstractUser):
    age = models.PositiveIntegerField(blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True)
    image = models.ImageField(upload_to='user_profile/', blank=True)
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions')

    def __str__(self):
        return self.username
    def save(self, *args, **kwargs):
        # Generate username based on email, last 4 digits of contact, and first name
        if not self.username:
            email_username = self.email.split('@')[0]  # Get string before '@' in email
            last_four_digits = re.search(r'\d{4}$', self.contact).group()  # Get last 4 digits of contact
            first_name_slug = slugify(self.first_name)  # Convert first name to a slug
            # Concatenate the above values to create a unique username
            username = f"{email_username}_{last_four_digits}_{first_name_slug}"
            # Ensure username is unique by appending numbers if necessary
            base_username = username
            counter = 1
            while Person.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            self.username = username
        super().save(*args, **kwargs)
    
class BankDetails(models.Model):
    user = models.OneToOneField(Person, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    routing_number = models.CharField(max_length=20)
    current_balance = models.FloatField(default=100)
    # Add more fields as needed

    def __str__(self):
        return f"Bank details for {self.user.username}"
