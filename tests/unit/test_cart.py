from django.conf import settings
from cart.cart import Cart
from mysite.models import Product, StoreUser
from django.test import RequestFactory, TestCase
from tests.constats_test import PRODUCT_PRICE, QUANTITY_AVAILABLE

class CartTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.session = {}
        self.cart = Cart(self.request)

    def test_cart_init(self):
        self.assertIn(settings.CART_SESSION_ID, self.request.session)
        self.assertIsInstance(self.cart.cart, dict)
        self.assertEqual(len(self.cart.cart), 0)
        
    def test_cart_init_with_cart(self):
        self.assertIn(settings.CART_SESSION_ID, self.request.session)
        self.assertIsInstance(self.cart.cart, dict)
        self.assertEqual(len(self.cart.cart), 0)
        
    def test_save_cart(self):
        self.cart.cart['1'] = {'quantity': 2, 'price': '100'}
        self.cart.save()
        self.assertIn(settings.CART_SESSION_ID, self.request.session)
        self.assertEqual(self.request.session[settings.CART_SESSION_ID], self.cart.cart) 
        
    def test_add_cart(self):
        quantity = 1
        product = Product.objects.create(name='test_name', price=PRODUCT_PRICE, quantity_available=QUANTITY_AVAILABLE)
        self.cart.add(product, quantity)
        self.assertIn(settings.CART_SESSION_ID, self.request.session)
        cart_product = {settings.CART_SESSION_ID: {str(product.pk): {'quantity': quantity, 'price': str(PRODUCT_PRICE)}}}
        self.assertEqual(self.request.session, cart_product)
        
    def test_remove_cart(self):
        quantity = 1
        product = Product.objects.create(name='test_name', price=PRODUCT_PRICE, quantity_available=QUANTITY_AVAILABLE)
        self.cart.add(product, quantity)
        self.cart.save()
        self.cart.remove(product)
        self.assertEqual(len(self.cart.cart), 0)
        
    def test_clear_cart(self):
        request = self.factory.get('/')
        request.session = {settings.CART_SESSION_ID: {'1': {'quantity': 2, 'price': '100'}}}
        cart = Cart(request)
        cart.clear()
        self.assertNotIn(settings.CART_SESSION_ID, request.session)