from django.contrib import admin
from .models import StoreUser, Product, Purchase, Return


admin.site.register(StoreUser)
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Return)
