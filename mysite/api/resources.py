from rest_framework.viewsets import ModelViewSet
from mysite.api.serializers import UserSerializer, ProductSerializer, PurchaseSerializer, ReturnSerializer
from mysite.models import StoreUser, Product, Purchase, Return

class ProductModelViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
class UserModelViewSet(ModelViewSet):
    queryset = StoreUser.objects.all()
    serializer_class = UserSerializer
    
class PurchaseModelViewSet(ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    
class ReturnModelViewSet(ModelViewSet):
    queryset = Return.objects.all()
    serializer_class = ReturnSerializer