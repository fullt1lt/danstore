from unittest.mock import patch
from django import forms
from django.test import RequestFactory, TestCase
from forms.forms import PurchaseForm
from mysite.models import Product, StoreUser
from tests.constats_test import PRODUCT_PRICE, QUANTITY_AVAILABLE

class PurchaseFormTestCase(TestCase):
    
    def setUp(self) -> None:
        self.user = StoreUser.objects.create(username="test", password='pass')
        self.request = RequestFactory().get('/')
        self.request.user = self.user
        self.product = Product.objects.create(name='test_name', price=PRODUCT_PRICE, quantity_available=QUANTITY_AVAILABLE)
        self.quantity = 5
        self.data = {'product_id': str(self.product.pk), "quantity": self.quantity}
    
    def test_purchase_form_init_empty_request(self):
        purf = PurchaseForm()
        self.assertIsNone(purf.request)
        
    def test_purchase_form_init_exist_request(self):
        request = RequestFactory().get('/')
        purf = PurchaseForm(request=request)
        self.assertEqual(purf.request, request)
        
    def test_clean(self):
        purf = PurchaseForm(self.data, request=self.request)
        purf.is_valid()
        purf.clean()
        self.assertEqual(purf.clean(), {"quantity": self.quantity})
        self.assertEqual(purf.product, self.product)
        self.assertEqual(purf.quantity, self.quantity)
        
    def test_check_product_exist(self):
        data = {'product_id': str(self.product.pk), "quantity": self.quantity}
        purf = PurchaseForm(data, request=self.request)
        self.assertEqual(purf.check_product_exist(), self.product)
        
    @patch('forms.forms.messages')
    def test_check_product_exist_without_product(self, mock_messages):
        mock_messages.error.return_value = ""
        data = {"quantity": self.quantity}
        purf = PurchaseForm(data, request=self.request)
        with self.assertRaises(forms.ValidationError):
            purf.check_product_exist()
            
    @patch('forms.forms.messages')
    def test_check_product_exist_incorect_product_id(self, mock_messages):
        mock_messages.error.return_value = ""
        data = {'product_id': "10", "quantity": self.quantity}
        purf = PurchaseForm(data, request=self.request)
        with self.assertRaises(forms.ValidationError):
            purf.check_product_exist()
            
    def test_check_quantity_valid(self):
        data = {'product_id': str(self.product.pk), "quantity": self.quantity}
        purf = PurchaseForm(data, request=self.request)
        self.assertIsNone(purf.check_quantity(self.quantity, self.product))
        
    @patch('forms.forms.messages')
    def test_check_quantity_invalid(self, mock_messages):
        mock_messages.error.return_value = ""
        quantity = 101 
        data = {'product_id': str(self.product.pk), "quantity": quantity}
        purf = PurchaseForm(data, request=self.request)
        with self.assertRaises(forms.ValidationError):
            purf.check_quantity(quantity, self.product)
        self.assertTrue(purf.errors)
        self.assertIn('__all__', purf.errors)
        
    def test_check_wallet_valid(self):
        data = {'product_id': str(self.product.pk), "quantity": self.quantity}
        purf = PurchaseForm(data, request=self.request)
        self.assertIsNone(purf.check_wallet(self.quantity, self.product))
        
    @patch('forms.forms.messages')
    def test_check_wallet_invalid(self, mock_messages):
        mock_messages.error.return_value = ""
        quantity = 11
        data = {'product_id': str(self.product.pk), "quantity": quantity}
        purf = PurchaseForm(data, request=self.request)
        with self.assertRaises(forms.ValidationError):
            purf.check_wallet(quantity, self.product)
        self.assertTrue(purf.errors)
        self.assertIn('__all__', purf.errors)