from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, CreateView
from danstore.forms import RegisterUserForm

class Login(LoginView):
    next_page = '/'
    template_name = 'login.html'
    redirect_authenticated_user = True
    

class Register(CreateView):
    form_class = RegisterUserForm
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