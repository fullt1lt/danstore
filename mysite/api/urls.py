from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from mysite.api.resources import ProductModelViewSet, PurchaseModelViewSet, RegisterApiView, ReturnModelViewSet, UserModelViewSet


router = routers.DefaultRouter()
router.register(r'products', ProductModelViewSet)
router.register('users', UserModelViewSet)
router.register('purchases', PurchaseModelViewSet)
router.register('returns', ReturnModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', obtain_auth_token, name='auth_token'),
    path('register/', RegisterApiView.as_view(), name='register'),
]