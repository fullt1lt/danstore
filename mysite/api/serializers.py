from rest_framework import serializers
from mysite.models import StoreUser, Product, Purchase, Return
from django.db.models import Q
from django.core.validators import MinValueValidator


class RegisterSerializer(serializers.ModelSerializer):
    password =  serializers.CharField(write_only=True)

    class Meta:
        model = StoreUser
        fields = ['username', 'email', 'password']
        
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        user_exist = Q(username__iexact=username) | Q(email__iexact=email)
        if StoreUser.objects.filter(user_exist).exists():
            raise serializers.ValidationError('Username or email already exists')
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        return StoreUser.objects.create_user(password=password, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StoreUser
        fields = ['id','username', 'email', 'wallet']


class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'quantity_available']
        
        
class PurchaseSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(required=True, validators=[MinValueValidator(1)])
    class Meta:
        model = Purchase
        fields = ['id', 'product', 'quantity',]
        
    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity')
        user = self.context['request'].user
        if product.quantity_available < quantity:
            raise serializers.ValidationError('Not enough quantity')
        if user.wallet < product.price * quantity:
            raise serializers.ValidationError('Not enough money on the cart')
        return attrs

class ReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Return
        fields = ['id', 'purchase', 'price_purchase']
        
    def validate(self, attrs):
        purchase = attrs.get('purchase')
        user = self.context['request'].user
        if purchase.user != user:
            raise serializers.ValidationError('It is not your purchase')
        if purchase.not_returnable:
            raise serializers.ValidationError('This purchase is not returnable')
        return attrs
        