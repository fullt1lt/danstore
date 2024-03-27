from django.shortcuts import render
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, CreateView

class Login(LoginView):
    next_page = '/'
    template_name = 'login.html'
    
# class Logout(LogoutView):
#     next_page = '/'
#     login_url = 'login/' 
    
class Register(CreateView):
    form_class = UserCreationForm
    template_name = 'register.html'
    success_url = '/'

class HomePage(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')
    
class ProductPage(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, 'product.html')

class AboutPage(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, 'about.html')