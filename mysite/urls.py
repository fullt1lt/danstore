from django.urls import path
from mysite.views import AboutPage, AdminPageView, CreateProductView, HomePage, Login, ProductDeleteView, ProductPage, ProductUpdateView, Register
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
]