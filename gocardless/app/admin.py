from django.contrib import admin
from .models import Person, BankDetails

admin.site.register(Person)
admin.site.register(BankDetails)