from django.shortcuts import get_object_or_404
from django.contrib import messages
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import CreateAPIView
from cart.cart import Cart
from danstore.settings import CART_COOKIE
from mysite.api.permissions import IsAdminOrReadOnly, ReturnFromAdmin
from mysite.api.serializers import RegisterSerializer, UserSerializer, ProductSerializer, PurchaseSerializer, ReturnSerializer
from mysite.models import StoreUser, Product, Purchase, Return
from rest_framework.decorators import action
from django.db import transaction


class RegisterApiView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes =[]
    queryset = StoreUser.objects.all()


class ProductModelViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    

class UserModelViewSet(ModelViewSet):
    queryset = StoreUser.objects.all()
    serializer_class = UserSerializer
    

class PurchaseModelViewSet(ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    http_method_names = ['get', 'post']
    
    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        user = self.request.user
        product.quantity_available -= quantity
        user.wallet -= product.price * quantity
        with transaction.atomic(): 
            product.save()
            user.save()
            serializer.save(user=self.request.user)
    

class ReturnModelViewSet(ModelViewSet):
    queryset = Return.objects.all()
    serializer_class = ReturnSerializer
    http_method_names = ['get', 'post']
    permission_classes = [ReturnFromAdmin]
    
    def get_queryset(self):
        if not self.request.user.is_superuser:
            return Return.objects.filter(purchase__user=self.request.user)
        return Return.objects.all()
    
    @action(methods=['post'], detail=True)
    def approve(self, request, pk=None):
        ret = self.get_object()
        purchase = ret.purchase
        product = purchase.product
        user = purchase.user
        quantity = purchase.quantity
        user.wallet += ret.price_purchase
        product.quantity_available += quantity
        with transaction.atomic():
            product.save()
            user.save()
            ret.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['post'], detail=True)
    def decline(self):
        ret = self.get_object()
        ret.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)