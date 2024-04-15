from cart.cart import Cart
from django.utils.deprecation import MiddlewareMixin

 
class CartMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        request.cart = Cart(request)