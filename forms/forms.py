from django.contrib import messages
from django import forms
from danstore.settings import PURCHASE_RETURN_TIME
from mysite.models import Product, Return, StoreUser, Purchase
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone
      
class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Name'}))
    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))
    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class': 'form-input','placeholder': 'Confirm password'}))

    class Meta:
        model = StoreUser
        fields = ('username', 'password1', 'password2')
        
class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Name'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))
    
    class Meta:
        model = StoreUser
        fields = ('username', 'password')
        
        
class ProductForm(forms.ModelForm):
    name = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'create_name', 'placeholder': 'Name'}))
    description = forms.CharField(label='', widget=forms.Textarea(attrs={'class': 'create_description', 'rows': 8, 'placeholder': 'Description'}))
    price = forms.DecimalField(label='', widget=forms.NumberInput(attrs={'class': 'create_price', 'placeholder': 'Price'}))
    quantity_available = forms.IntegerField(label='', widget=forms.NumberInput(attrs={'class': 'create_quantity', 'placeholder': 'Quantity available'}))
    image = forms.ImageField(label='', widget=forms.FileInput(attrs={'class': 'create_image'}))
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'quantity_available', 'image']
        

class PurchaseForm(forms.ModelForm):
    
    class Meta:
        model = Purchase
        fields = ('quantity',)
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        product = self.check_product_exist()
        self.check_quantity(quantity, product)
        self.check_wallet(quantity, product)
        self.product = product
        self.quantity = quantity
        return cleaned_data
           
    def check_product_exist(self):
        product_id = self.data.get('product_id')
        try:
            return Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(self.request, "Product does not exist", extra_tags=str(product_id))
            raise forms.ValidationError("Product does not exist")
    
    def check_quantity(self, quantity, product):
        if quantity > product.quantity_available:
            messages.error(self.request, "Not enough quantity available", extra_tags=str(product.id))
            self.add_error(None, "Not enough quantity available")
            raise forms.ValidationError("Not enough quantity available")
    
    def check_wallet(self, quantity, product):
        if quantity * product.price > self.request.user.wallet:
            messages.error(self.request, "Insufficient funds", extra_tags=str(product.id))
            self.add_error(None, "Insufficient funds")
            raise forms.ValidationError("Insufficient funds")
            

class ReturnForm(forms.ModelForm):
    
    class Meta:
        model = Return
        exclude = ['purchase',]
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        
    def clean(self):

        request = self.request
        purchase_id = self.data.get('purchase_id')
        try:
            purchase = Purchase.objects.get(pk=purchase_id)
        except Purchase.DoesNotExist:
            messages.error(request, "Purchase does not exist")
            raise forms.ValidationError("Purchase does not exist")
        if (timezone.now() - purchase.purchase_time).seconds > PURCHASE_RETURN_TIME:
            messages.error(request, "Return time has expired", extra_tags=str(purchase.id))
            self.add_error(None, "Return time has expired")
        self.purchase = purchase
        self.price_purchase = purchase.product.price