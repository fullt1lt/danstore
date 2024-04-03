from django import forms
from mysite.models import Product, StoreUser
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