from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models


class StoreUser(AbstractUser):
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=10000)

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity_available = models.PositiveIntegerField()
    image = models.ImageField(blank=True, upload_to="images/")
    
    def __str__(self) -> str:
        return self.name

class Purchase(models.Model):
    user = models.ForeignKey(StoreUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_time = models.DateTimeField(auto_now_add=True)

class Return(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    request_time = models.DateTimeField(auto_now_add=True)