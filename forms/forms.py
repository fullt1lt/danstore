from django.contrib import messages
from django import forms
from mysite.models import Product, StoreUser, Purchase
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
      
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
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        
        
    def clean(self):
        cleaner_data = super().clean()
        quantity = cleaner_data.get('quantity')
        request = self.request
        product_id = self.data.get('product_id')
        try:
            product = Product.objects.get(pk=product_id)
        except product.DoesNotExist:
            messages.error(request, "Product does not exist", extra_tags=str(product.id))
            raise forms.ValidationError("Product does not exist")
        purchase = Purchase.objects.filter(user=request.user, product=product).first()
        purchase_quantity = self.preparation_purchase_quantity(purchase)
        
        if product.quantity_available <= quantity and product.quantity_available <= quantity + purchase_quantity:
            messages.error(request, "Not enough quantity available", extra_tags=str(product.id))
            self.add_error(None, "Not enough quantity available")
        self.product = product
        self.quantity = quantity
            
    def preparation_purchase_quantity(self, purchase):
        if purchase is None:
            return 0
        else:
            return purchase.quantity