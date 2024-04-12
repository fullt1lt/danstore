from django.urls import path
from django.contrib.auth.views import LogoutView
from mysite.views import (AboutPage, AddToPurchaseView, AdminPageView, CreateProductView, CheckoutView, HomePage, Login, 
                          ProductDeleteView, ProductPage, ProductUpdateView, Register, RemoveFromPurchaseView, ViewCartView,
                          PurchaseHistoryView, AddToPPurchaseHistoryView, AdminReturnView, DeleteReturnView, ConfirmReturnView, AddToCartView)

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
    path('remove_from_purchase/<int:purchase_item_id>/', RemoveFromPurchaseView.as_view(), name='remove_from_purchase'),
    path('complete_purchase/<int:product_id>/', CheckoutView.as_view(), name='complete_purchase'),
    path('purchase_history/', PurchaseHistoryView.as_view(), name='purchase_history'),
    path('admin_return/', AdminReturnView.as_view(), name='admin_return'),
    path('add_to_purchase_history/<int:history_item_id>/', AddToPPurchaseHistoryView.as_view(), name='add_to_purchase_history'),
    path('delete_return/<int:pk>/', DeleteReturnView.as_view(), name='delete_return'),
    path('confirm_return/<int:item_id>/<int:product_id>/<int:user_id>', ConfirmReturnView.as_view(), name='confirm_return'),

]