from django.urls import path
from mysite.views import AboutPage, AddToPurchaseView, AdminPageView, CreateProductView, CheckoutView, HomePage, Login, ProductDeleteView, ProductPage, ProductUpdateView, Register, RemoveFromPurchaseView, ViewPurchaseView
from django.contrib.auth.views import LogoutView

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
    path('add_to_purchase/<int:product_id>/', AddToPurchaseView.as_view(), name='add_to_purchase'),
    path('remove_from_purchase/<int:purchase_item_id>/', RemoveFromPurchaseView.as_view(), name='remove_from_purchase'),
    path('purchase/', ViewPurchaseView.as_view(), name='purchase'),
     path('complete_purchase/<int:product_id>/', CheckoutView.as_view(), name='complete_purchase'),
]