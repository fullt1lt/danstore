from django.contrib import messages
from django.db import transaction
from django.forms import ValidationError
from django.http import Http404
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import  login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, DeleteView, UpdateView,CreateView
from cart.cart import Cart
from danstore.mixins import SuperUserRequiredMixin
from forms.forms import LoginUserForm, ProductForm, PurchaseForm, RegisterUserForm, ReturnForm
from mysite.models import Product, Purchase, Return


class Login(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return reverse_lazy('admin_page')
        else:
            return reverse_lazy('index')
        
class Register(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = '/'
    
    def form_valid(self, form):
        result = super().form_valid(form=form)
        login(self.request, self.object)
        return result
    
     
class HomePage(ListView):
    paginate_by = 6
    template_name = 'index.html'
    queryset = Product.objects.all()
    extra_context = {"form": PurchaseForm}
    ordering = ['-name']
    
    
class ProductPage(LoginRequiredMixin, ListView):
    
    login_url = reverse_lazy('login') 
    
    def get(self, request, *args, **kwargs):
        return render(request, 'product.html')


class AboutPage(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, 'about.html')
    

class CreateProductView(SuperUserRequiredMixin,View):
    def get(self, request):
        form = ProductForm()
        return render(request, 'add_product.html', {'form': form})

    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_product')
        return render(request, 'add_product.html', {'form': form})
    

class AdminPageView(SuperUserRequiredMixin,ListView):
    paginate_by = 6
    template_name = 'admin_page.html'
    queryset = Product.objects.all()
    

class ProductDeleteView(LoginRequiredMixin,SuperUserRequiredMixin, DeleteView):
    model = Product
    success_url = '/admin_page/'
    
    
class ProductUpdateView(SuperUserRequiredMixin,UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_update.html'
    
    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('admin_page')


class AddToPurchaseView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    queryset = Product.objects.all()
    form_class = PurchaseForm
    success_url = '/'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        purchase = form.save(commit=False)
        cart = Cart(self.request)
        user = self.request.user
        product = form.product
        purchase.user = user
        purchase.product = product
        product.quantity_available -= purchase.quantity
        user.wallet -= purchase.quantity * product.price
        with transaction.atomic():
            user.save()
            product.save()
            purchase.save()
            cart.remove(product)
        return super().form_valid(form=form)
    
    
    def form_invalid(self, form) :
        return redirect('cart')
        
    
class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        product = self.check_product_exist()
        if product is not None:
            self.check_quantity(product)
        return redirect('/')

    def check_product_exist(self):
        product_id = self.request.POST.get('product_id')
        try:
            return Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(self.request, "Product does not exist", extra_tags=str(product_id))
        
    def check_quantity(self, product):
        quantity = int(self.request.POST.get('quantity', 1))
        cart = Cart(self.request)
        if quantity > product.quantity_available or self.check_quantity_in_cart(quantity, product, cart):
            messages.error(self.request, "Not enough quantity available", extra_tags=str(product.id))
        else:
            cart.add(product, quantity)

    def check_quantity_in_cart(self, quantity, product, cart):
        product_id = str(product.id)
        if product_id in cart.cart:
            cart_product = cart.cart[product_id]
            if quantity + cart_product['quantity'] > product.quantity_available:
                return True
        return False


class RemoveFromPurchaseView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            cart = Cart(request)
            cart.remove(product)
        except Product.DoesNotExist:
            messages.error(request, 'Product not found in cart.',  extra_tags=product_id)
        return redirect('cart')


class ViewCartView(LoginRequiredMixin, ListView):    
    def get(self, request):
        cart = Cart(request)
        products = []
        for key, value in cart.cart.items():
            try:
                product = Product.objects.get(id=key)
                product.quantity_cart = value['quantity']
                product.total_price = value['quantity'] * product.price
                products.append(product)
            except product.DoesNotExist:
                pass
        return render(request, 'purchase.html', {'products': products})


class PurchaseHistoryView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = "purchase_history.html"
    context_object_name = "purchase_history_items"

    def get_queryset(self):
        purchases_list = []
        purchases = Purchase.objects.filter(user=self.request.user)
        for purchase in purchases:
            purchase.total_price = purchase.product.price * purchase.quantity
            purchases_list.append(purchase)
        return purchases_list
    
    
class AddToReturnView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    form_class = ReturnForm
    success_url = reverse_lazy('purchase_history')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        ret = form.save(commit=False)
        ret.purchase = form.purchase
        ret.price_purchase = form.price_purchase
        ret.save()
        return super().form_valid(form=form)
    
    
    def form_invalid(self, form) :
        print(form.errors)
        return redirect('purchase_history')


@method_decorator(staff_member_required, name='dispatch')
class AdminReturnView(ListView):
    model = Return
    template_name = "admin_return.html"
    context_object_name = "admin_return_items"
    
    def get_queryset(self):
        return_list = []
        ret = Return.objects.all()
        for ret_item in ret:
            ret_item.total_price = ret_item.purchase.quantity * ret_item.price_purchase
            return_list.append(ret_item)
        return return_list

    
class DeleteReturnView(LoginRequiredMixin,SuperUserRequiredMixin, DeleteView):
    model = Return
    success_url = '/admin_return/'


class ConfirmReturnView(LoginRequiredMixin,SuperUserRequiredMixin, DeleteView):
    model = Return
    success_url = '/admin_return/'
    
    def form_valid(self, form):
        ret = self.object
        product = ret.purchase.product
        user = ret.purchase.user
        product.quantity_available += ret.purchase.quantity
        user.wallet += product.price * ret.purchase.quantity
        with transaction.atomic():
            product.save()
            user.save()
            return super().form_valid(form=form)