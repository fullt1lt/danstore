from rest_framework import serializers
from mysite.models import StoreUser, Product, Purchase, Return

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StoreUser
        fields = ['id',]


class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'quantity_available']
        
        
class PurchaseSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    product = ProductSerializer()
    class Meta:
        model = Purchase
        fields = ['id', 'user', 'product', 'quantity', 'purchase_time']
        

class ReturnSerializer(serializers.ModelSerializer):
    purchase = PurchaseSerializer()
    class Meta:
        model = Return
        fields = ['id', 'purchase', 'price_purchase']