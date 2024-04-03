from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, FormView, DeleteView, UpdateView
from forms.forms import LoginUserForm, ProductForm, RegisterUserForm
from mysite.models import Product

class Login(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return reverse_lazy('admin_page')
        else:
            return reverse_lazy('index')

class Register(FormView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = '/'
    
    def form_valid(self, form):
        user = form.save(commit=False)
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
    paginate_by = 8
    template_name = 'index.html'
    queryset = Product.objects.all()
    
    
class ProductPage(LoginRequiredMixin, ListView):
    
    login_url = reverse_lazy('login') 
    
    def get(self, request, *args, **kwargs):
        return render(request, 'product.html')


class AboutPage(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, 'about.html')
    

@method_decorator(staff_member_required, name='dispatch')
class CreateProductView(View):
    def get(self, request):
        form = ProductForm()
        return render(request, 'add_product.html', {'form': form})

    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_product')
        return render(request, 'add_product.html', {'form': form})
    

@method_decorator(staff_member_required, name='dispatch')
class AdminPageView(ListView):
    paginate_by = 8
    template_name = 'admin_page.html'
    queryset = Product.objects.all()
    
    # def post(self, request, *args, **kwargs):
    #     product_id = request.POST.get('product_id')  # Получаем идентификатор продукта из POST запроса
    #     quantity = request.POST.get('quantity')  # Получаем новое количество товара из POST запроса

    #     if product_id and quantity:
    #         try:
    #             product = Product.objects.get(pk=product_id)
    #             product.quantity_available = quantity
    #             product.save() 
    #         except Product.DoesNotExist:
    #             # Обработка случая, если товар не найден
    #             pass
        
    #     return redirect('admin_page')


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    success_url = '/admin_page/'
    
    
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_update.html'
    
    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('admin_page')
