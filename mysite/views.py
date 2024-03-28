from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, CreateView
from danstore.forms import LoginUserForm, RegisterUserForm

class Login(LoginView):
    form_class = LoginUserForm
    next_page = '/'
    template_name = 'login.html'
    
class Register(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = '/'
    
    def form_valid(self, form):
        user = form.save(commit=False)  # Не сохраняем пользователя сразу
        password1 = form.cleaned_data['password1']
        password2 = form.cleaned_data['password2']

        if password1 == password2:  # Проверка совпадения паролей
            user.set_password(password1)
            user.save()

            # Автоматический вход пользователя
            user = authenticate(username=user.username, password=password1)
            login(self.request, user)

            return super().form_valid(form)
        else:
            # Если пароли не совпадают, вернуть сообщение об ошибке
            form.add_error('password2', 'Пароли не совпадают')
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class HomePage(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')
    
class ProductPage(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, 'product.html')

class AboutPage(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, 'about.html')