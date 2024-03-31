from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, CreateView, FormView
from forms.forms import LoginUserForm, RegisterUserForm
from mysite.models import Product

class Login(LoginView):
    form_class = LoginUserForm
    next_page = '/'
    template_name = 'login.html'

class Register(FormView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = '/'
    
    def form_valid(self, form):
        user = form.save(commit=False)  # Не сохраняем пользователя сразу
        password1 = form.cleaned_data['password1']
        password2 = form.cleaned_data['password2']
        if password1 == password2:  
            user.set_password(password1)
            user.save()
            user = authenticate(username=user.username, password=password1)
            login(self.request, user)

            return super().form_valid(form)
        else:
            form.add_error('password2', 'Пароли не совпадают')
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class HomePage(ListView):
    paginate_by = 5
    template_name = 'index.html'
    queryset = Product.objects.all()
    
    
class ProductPage(LoginRequiredMixin, ListView):
    
    login_url = reverse_lazy('login') 
    
    def get(self, request, *args, **kwargs):
        return render(request, 'product.html')


class AboutPage(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, 'about.html')