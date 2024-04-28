from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
import re
import os

class Person(AbstractUser):
    age = models.PositiveIntegerField(blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True)
    image = models.ImageField(upload_to='user_images/', blank=True)
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions')

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
       
        if not self.username:
            email_username = self.email.split('@')[0] 
            last_four_digits = re.search(r'\d{4}$', self.contact).group()  
            first_name_slug = slugify(self.first_name) 
            
            username = f"{email_username}_{last_four_digits}_{first_name_slug}"
            
            base_username = username
            counter = 1
            while Person.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            self.username = username
        
        
        filename = ''
        
        if self.image:
            filename = f"{self.email}_{self.contact}_{slugify(self.first_name)}"
            self.image.name = self.image.field.upload_to + filename + os.path.splitext(self.image.name)[1]
        
        super().save(*args, **kwargs)
    
class BankDetails(models.Model):
    user = models.OneToOneField(Person, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    current_balance = models.FloatField(default=100)

    def __str__(self):
        return f"Bank details for {self.user.username}"
