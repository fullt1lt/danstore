from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from mysite.api.resources import ProductModelViewSet, PurchaseModelViewSet, ReturnModelViewSet, UserModelViewSet


router = routers.DefaultRouter()
router.register('products', ProductModelViewSet)
router.register('users', UserModelViewSet)
router.register('purchases', PurchaseModelViewSet)
router.register('returns', ReturnModelViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/', include(router.urls)),
]

from django.urls import path
from django.contrib.auth.views import LogoutView
from mysite.views import (AboutPage, AddToPurchaseView, AdminPageView, CreateProductView, HomePage, Login, 
                          ProductDeleteView, ProductPage, ProductUpdateView, Register, RemoveFromPurchaseView, ViewCartView,
                          PurchaseHistoryView, AddToReturnView, AdminReturnView, DeleteReturnView, ConfirmReturnView, AddToCartView)

urlpatterns = [
    path('', HomePage.as_view(), name='index'),
    path('product/', ProductPage.as_view(), name='product'),
    path('login/', Login.as_view(), name='login'),
    path('about/', AboutPage.as_view(), name='about'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin_page/', AdminPageView.as_view(), name='admin_page'),
    path('add_product/', CreateProductView.as_view(), name='add_product'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    path('product/update/<int:pk>/', ProductUpdateView.as_view(), name='product_update'),
    path('cart/', ViewCartView.as_view(), name='cart'),
    path('add-to-cart/', AddToCartView.as_view(), name='add_to_cart'),
    path('add_to_purchase/', AddToPurchaseView.as_view(), name='add_to_purchase'),
    path('remove_from_purchase/<int:product_id>/', RemoveFromPurchaseView.as_view(), name='remove_from_purchase'),
    path('purchase_history/', PurchaseHistoryView.as_view(), name='purchase_history'),
    path('admin_return/', AdminReturnView.as_view(), name='admin_return'),
    path('add-to-return', AddToReturnView.as_view(), name='add_to_return'),
    path('delete_return/<int:pk>/', DeleteReturnView.as_view(), name='delete_return'),
    path('confirm_return/<int:pk>/>', ConfirmReturnView.as_view(), name='confirm_return'),
]