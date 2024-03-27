from django.contrib import admin
from .models import UserProfile, Product, Purchase, Return
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Return)