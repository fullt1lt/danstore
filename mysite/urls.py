from django.urls import path
from mysite.views import AboutPage, HomePage, Login, ProductPage, Register
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', HomePage.as_view(), name='index'),
    path('product/', ProductPage.as_view(), name='product'),
    path('login/', Login.as_view(), name='login'),
    path('about/', AboutPage.as_view(), name='about'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]