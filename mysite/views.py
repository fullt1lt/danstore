from django.contrib import messages
from django.db import transaction
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, FormView, DeleteView, UpdateView, TemplateView,CreateView
from forms.forms import LoginUserForm, ProductForm, PurchaseForm, RegisterUserForm
from mysite.models import Product, Purchase, PurchaseHistory, Return, StoreUser
from django.utils import timezone
from datetime import timedelta


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
        purchase.user = self.request.user
        purchase.product = form.product
        purchase.save()
        return super().form_valid(form=form)
    
    
    def form_invalid(self, form) :
        return redirect('/')

    
    def preparation_purchase_(self, purchase):
        if purchase is None:
            return 0
        else:
            return purchase.quantity
            

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
        purchase = Purchase.objects.filter(user=request.user).first()
        product = Product.objects.filter(id=product_id).first()
        with transaction.atomic():
            price_purchase +=(purchase.quantity * product.price)
            if price_purchase <= request.user.wallet:
                PurchaseHistory.objects.create(user=request.user, product=product ,quantity=purchase.quantity, price_purchase=price_purchase)
                purchase.product.quantity_available -= purchase.quantity
                request.user.wallet -= price_purchase
                purchase.product.save()
                request.user.save() 
                purchase.delete()
            else:
                error_message = 'Purchase is not possible'
                messages.error(request, error_message, extra_tags=str(product.id))
        return redirect('purchase')


class PurchaseHistoryView(LoginRequiredMixin, ListView):
    model = PurchaseHistory
    template_name = "purchase_history.html"
    context_object_name = "purchase_history_items"

    def get_queryset(self):
        return PurchaseHistory.objects.filter(user=self.request.user)
    

class AddToPPurchaseHistoryView(View):
    
    def post(self, request, history_item_id):
        messages.error(request, self.check_order(history_item_id), extra_tags=str(history_item_id))
        return redirect('purchase_history')
        
    def add_return_order(self, history_item):
        Return.objects.create(purchase=history_item)
        
    def check_order(self, history_item_id):
        history_item = PurchaseHistory.objects.get(id=history_item_id)
        message = self.check_order_exists(history_item)
        if message == None:
            return self.check_order_time(history_item)
        else:
            return message
        
    def check_order_exists(self, history_item):
        if Return.objects.filter(purchase=history_item).exists():
            return 'Return purchase already exists.'
        else:
            return None
        
    def check_order_time(self, history_item):
        if timezone.now() - history_item.purchase_history_time < timedelta(minutes=3):
            self.add_return_order(history_item)
            return 'Return purchase submitted.'
        else:
            return 'Time to return has expired.'


@method_decorator(staff_member_required, name='dispatch')
class AdminReturnView(ListView):
    model = Return
    template_name = "admin_return.html"
    context_object_name = "admin_return_items"

    def get_queryset(self):
        return Return.objects.all()

    
class DeleteReturnView(LoginRequiredMixin, DeleteView):
    model = Return
    success_url = '/admin_return/'


class ConfirmReturnView(LoginRequiredMixin, View):
    
    def post(self, request, item_id, product_id, user_id):
        ret = Return.objects.filter(id=item_id).first()
        with transaction.atomic():
            self.confirm_return_product(product_id, ret)
            self.confirm_return_money(user_id, ret)
            ret.delete()
        return redirect('admin_return')
    
    def confirm_return_money(self, user_id, ret):
        user = StoreUser.objects.filter(id=user_id).first()
        user.wallet += ret.purchase.price_purchase
        user.save()
        
    def confirm_return_product(self, product_id, ret):
        product = Product.objects.filter(id=product_id).first()
        product.quantity_available +=ret.purchase.quantity
        product.save()