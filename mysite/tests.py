from django.test import TestCase


# Create your tests here.

class TestFake(TestCase):

    def test_fake(self):
        assert True

    def test_fail(self):
        assert False
