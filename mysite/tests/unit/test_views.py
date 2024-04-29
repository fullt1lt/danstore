from django.test import RequestFactory, TestCase
from forms.forms import PurchaseForm


class AddToPurchaseViewTestCase(TestCase):
    
    def test_get_form_kwargs(self):
        request = RequestFactory().get('/')
        view = PurchaseForm
        view.setup(request)
        context = view.get_form_kwargs()
        self.assertIn('request', context)