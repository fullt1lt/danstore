from django.contrib import messages
from django.db import transaction
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, FormView, DeleteView, UpdateView, TemplateView
from forms.forms import LoginUserForm, ProductForm, RegisterUserForm
from mysite.models import Product, Purchase, PurchaseHistory
from django.db.models import Sum


class HomePageView(LoginRequiredMixin, ListView):
    template_name = "base.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchase_items'] = Purchase.objects.filter(user=self.request.user)
        return context
    

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
    paginate_by = 6
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
    paginate_by = 6
    template_name = 'admin_page.html'
    queryset = Product.objects.all()
    

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


class AddToPurchaseView(LoginRequiredMixin,View):
    login_url = reverse_lazy('login')
    
    def get(self, request, product_id):
        user = request.user
        quantity = self.preparation_quntity(request)
        product = get_object_or_404(Product, id=product_id)
        purchase_quantity = Purchase.objects.filter(user=user, product=product).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        error_message = self.add_to_purchase(user, quantity, product, purchase_quantity)
        messages.error(request, error_message, extra_tags=str(product.id))
        return redirect('index')
    
    def preparation_quntity(self,request):
        quantity_str = request.GET.get('quantity', '1')
        try:
            return max(int(quantity_str), 1)
        except ValueError:
            return 1
        
    def add_to_purchase(self,user, quantity, product, purchase_quantity):
        if purchase_quantity is None:
            purchase_quantity = 0
        if product.quantity_available >= quantity and product.quantity_available >= quantity + purchase_quantity:
            with transaction.atomic():
                purchase_item, created = Purchase.objects.get_or_create(
                    user=user,
                    product=product,
                    defaults={'quantity': quantity}
                )
                if not created:
                    purchase_item.quantity += quantity
                    purchase_item.save()
                return None
        else:
            return 'There are not enough products in stock.'
        
    

class RemoveFromPurchaseView(LoginRequiredMixin, View):
    def post(self, request, purchase_item_id):
        try:
            purchase_item = Purchase.objects.get(id=purchase_item_id)
            purchase_item.delete()
            messages.success(request, 'The product has been successfully removed from the cart.')
        except Purchase.DoesNotExist:
            messages.error(request, 'Product not found in cart.')
        
        return redirect('purchase')

class ViewPurchaseView(LoginRequiredMixin, ListView):    
    def get(self, request):
        purchase_items = Purchase.objects.filter(user=request.user)
        for purchase_item in purchase_items:
            purchase_item.total_price = purchase_item.quantity * purchase_item.product.price
        return render(request, 'purchase.html', {'purchase_items': purchase_items})
    
    
class CheckoutView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        price_purchase = 0
        purchase_items = Purchase.objects.filter(user=request.user)
        product = get_object_or_404(Product, id=product_id)
        with transaction.atomic():
            for item in purchase_items:
                price_purchase = +(item.quantity*product.price)
                if price_purchase <= request.user.wallet:
                    PurchaseHistory.objects.create(user=request.user, product=product ,quantity=item.quantity, price_purchase=price_purchase)
                    item.product.quantity_available -= item.quantity
                    request.user.wallet -= price_purchase
                    item.product.save()
                    request.user.save() 
                    purchase_items.delete()
                else:
                    error_message = 'Purchase is not possible'
                    messages.error(request, error_message, extra_tags=str(product.id))
        return redirect('purchase')
    
class PurchaseHistoryView(LoginRequiredMixin, ListView):
    model = PurchaseHistory
    template_name = "purchase_history.html"
    context_object_name = "purchase_history_items"  # Имя переменной контекста для списка объектов

    def get_queryset(self):
        return PurchaseHistory.objects.filter(user=self.request.user)