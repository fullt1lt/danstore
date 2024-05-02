from unittest.mock import patch
from django.conf import settings
from django.test import RequestFactory, TestCase
from cart.cart import Cart
from forms.forms import PurchaseForm
from mysite.models import Product, Purchase, StoreUser
from mysite.views import AddToCartView, AddToPurchaseView
from tests.constats_test import PRODUCT_PRICE, QUANTITY_AVAILABLE, USER_WALLET


class AddToPurchaseViewTestCase(TestCase):
    
    def test_get_form_kwargs(self):
        request = RequestFactory().get('/')
        view = AddToPurchaseView()
        view.setup(request)
        context = view.get_form_kwargs()
        self.assertIn('request', context)
        
    def test_form_valid(self):
        user = StoreUser.objects.create(username="test", password='pass')
        request = RequestFactory().post('/')
        request.user = user
        request.session = {}
        cart = Cart(request)
        product = Product.objects.create(name='test_name', price=PRODUCT_PRICE, quantity_available=QUANTITY_AVAILABLE)
        quantity = 1
        cart.add(product, quantity)
        data = {'product_id': str(product.pk), "quantity": quantity }
        purf = PurchaseForm(data, request=request)
        purf.is_valid()
        view = AddToPurchaseView()
        view.setup(request)
        response = view.form_valid(form=purf)
        purchase = view.object
        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(purchase, Purchase)
        self.assertEqual(purchase.quantity, quantity)
        self.assertEqual(purchase.product, product)
        self.assertEqual(purchase.product.quantity_available, product.quantity_available - quantity)
        self.assertEqual(request.user.wallet, USER_WALLET - (quantity * product.price))
        self.assertEqual(cart.cart, {})
        
    @patch('forms.forms.messages')
    def test_form_valid_does_not_product(self, mock_messages):
        mock_messages.error.return_value = ""
        user = StoreUser.objects.create(username="test", password='pass')
        request = RequestFactory().post('/')
        request.user = user
        request.session = {}
        cart = Cart(request)
        product = Product.objects.create(name='test_name', price=PRODUCT_PRICE, quantity_available=QUANTITY_AVAILABLE)
        quantity = 1
        cart.add(product, quantity)
        data = {'product_id': '45', "quantity": quantity }
        purf = PurchaseForm(data, request=request)
        view = AddToPurchaseView()
        view.setup(request)
        response = view.form_invalid(form=purf)
        self.assertEqual(response.status_code, 302)
        
        
class AddToCartViewTestCase(TestCase):
    
    def setUp(self):
        self.user = StoreUser.objects.create(username="test", password='pass')
        self.factory = RequestFactory()
        self.product = Product.objects.create(name='test_name', price=PRODUCT_PRICE, quantity_available=QUANTITY_AVAILABLE)
    
    @patch('mysite.views.messages')
    def test_check_product_exist(self,mock_messages):
        mock_messages.error.return_value = ""
        request = self.factory.post('/', {'product_id': str(self.product.pk)})
        request.user = self.user
        view = AddToCartView()
        view.request = request
        self.assertIsNotNone(view.check_product_exist())
        self.assertEqual(view.check_product_exist(), self.product)

    @patch('mysite.views.messages')
    def test_check_product_does_not_exist(self,mock_messages):
        mock_messages.error.return_value = ""
        request = self.factory.post('/', {'product_id': '112'})
        request.user = self.user
        view = AddToCartView()
        view.request = request
        self.assertIsNone(view.check_product_exist())

    def test_check_quantity_in_cart_exceeds_available_quantity(self):
        request = self.factory.post('/')
        view = AddToCartView()
        request.user = self.user
        request.session = {}
        view.request = request
        product = Product.objects.create(name='Test Product', price=PRODUCT_PRICE, quantity_available=5)
        cart = Cart(request)
        cart.cart = {str(product.pk): {'quantity': 4, 'price': PRODUCT_PRICE}}
        quantity = 2
        result = view.check_quantity_in_cart(quantity, product, cart)
        self.assertTrue(result)
        
    def test_check_quantity_in_cart_available_quantity(self):
        request = self.factory.post('/')
        view = AddToCartView()
        request.user = self.user
        request.session = {}
        view.request = request
        product = Product.objects.create(name='Test Product', price=PRODUCT_PRICE, quantity_available=5)
        cart = Cart(request)
        cart.cart = {str(product.pk): {'quantity': 4, 'price': PRODUCT_PRICE}}
        quantity = 1
        result = view.check_quantity_in_cart(quantity, product, cart)
        self.assertFalse(result)

    def test_check_quantity_in_cart_invalid_product_id(self):
        request = self.factory.post('/')
        view = AddToCartView()
        request.user = self.user
        request.session = {}
        view.request = request
        product = Product.objects.create(name='Test Product', price=PRODUCT_PRICE, quantity_available=5)
        cart = Cart(request)
        cart.cart = {'475': {'quantity': 4, 'price': PRODUCT_PRICE}}
        quantity = 2
        result = view.check_quantity_in_cart(quantity, product, cart)
        self.assertFalse(result)
        
    @patch('mysite.views.messages')
    def test_check_quantity_valid(self, mock_messages):
        mock_messages.error.return_value = ""
        quantity = 1
        product = Product.objects.create(name='Test Product', price=PRODUCT_PRICE, quantity_available=5)
        view = AddToCartView()
        request = self.factory.post('/', {'quantity': quantity})
        request.user = self.user
        request.session = {}
        view.request = request
        view.check_quantity(product)
        test_cart = {settings.CART_SESSION_ID: {str(product.pk): {'quantity': quantity, 'price': str(PRODUCT_PRICE)}}}
        self.assertEqual(request.session, test_cart)
        
    @patch('mysite.views.messages')
    def test_check_quantity_quantity_in_cart_is_more_than_product(self, mock_messages):
        mock_messages.error.return_value = ""
        quantity = 4
        product = Product.objects.create(name='Test Product', price=PRODUCT_PRICE, quantity_available=5)
        view = AddToCartView()
        request = self.factory.post('/', {'quantity': quantity})
        request.user = self.user
        request.session = {}
        view.request = request
        #Тут Мок метода check_quantity_in_cart -(в корзине уже есть товар и нельзя в корзину добавить больше чем товара на складе) 
        with patch.object(AddToCartView, 'check_quantity_in_cart', return_value=True):
            view.check_quantity(product)
            test_cart = {settings.CART_SESSION_ID: {}}
            self.assertEqual(request.session, test_cart)
            
    @patch('mysite.views.messages')
    def test_check_quantity_quantity_is_more_than_product(self, mock_messages):
        mock_messages.error.return_value = ""
        quantity = 6
        product = Product.objects.create(name='Test Product', price=PRODUCT_PRICE, quantity_available=5)
        view = AddToCartView()
        request = self.factory.post('/', {'quantity': quantity})
        request.user = self.user
        request.session = {}
        view.request = request
        view.check_quantity(product)
        test_cart = {settings.CART_SESSION_ID: {}}
        self.assertEqual(request.session, test_cart)
        
    def test_post_product_exists(self):
        quantity = 1
        product = Product.objects.create(name='Test Product', price=PRODUCT_PRICE, quantity_available=5)
        request = self.factory.post('/', {'product_id': product.id ,'quantity': quantity})
        request.user = self.user
        request.session = {}
        view = AddToCartView()
        view.request = request
        response = view.post(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        test_cart = {settings.CART_SESSION_ID: {str(product.pk): {'quantity': quantity, 'price': "{:.2f}".format(PRODUCT_PRICE)}}}
        self.assertEqual(request.session, test_cart)
    
    @patch('mysite.views.messages')
    def test_post_product_does_not_exists(self, mock_messages):
        mock_messages.error.return_value = ""
        quantity = 1
        product = Product.objects.create(name='Test Product', price=PRODUCT_PRICE, quantity_available=5)
        request = self.factory.post('/', {'product_id': '454' ,'quantity': quantity})
        request.user = self.user
        request.session = {}
        view = AddToCartView()
        view.request = request
        response = view.post(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertEqual(request.session, {})
        
    @patch('mysite.views.messages')
    def test_post_product_quantity_is_more_than_product(self,mock_messages):
        mock_messages.error.return_value = ""
        quantity = 6
        product = Product.objects.create(name='Test Product', price=PRODUCT_PRICE, quantity_available=5)
        request = self.factory.post('/', {'product_id': product.id ,'quantity': quantity})
        request.user = self.user
        request.session = {}
        view = AddToCartView()
        view.request = request
        response = view.post(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        test_cart = {settings.CART_SESSION_ID: {}}
        self.assertEqual(request.session, test_cart)
        
    
    @patch('mysite.views.messages')
    def test_post_product_quantity_in_cart_is_more_than_product(self,mock_messages):
        mock_messages.error.return_value = ""
        quantity = 1
        product = Product.objects.create(name='Test Product', price=PRODUCT_PRICE, quantity_available=5)
        request = self.factory.post('/', {'product_id': product.id ,'quantity': quantity})
        request.user = self.user
        product_in_cart = {settings.CART_SESSION_ID: {str(product.pk): {'quantity': 5, 'price': "{:.2f}".format(PRODUCT_PRICE)}}}
        request.session = product_in_cart
        view = AddToCartView()
        view.request = request
        response = view.post(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertEqual(request.session, product_in_cart)