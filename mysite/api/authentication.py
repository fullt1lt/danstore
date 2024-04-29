from rest_framework.authentication import TokenAuthentication
from django.utils.timezone import now
from danstore.settings import TIME_LIFETIME
from rest_framework.exceptions import AuthenticationFailed


class TokenExpiredAuthentication(TokenAuthentication):
    
    def authenticate(self, request):
        try:
            user, token = super().authenticate(request)
        except TypeError:
            return
        if (now() - token.created).seconds > TIME_LIFETIME:
            token.delete()
            raise AuthenticationFailed("The token's lifetime has expired")
        return user, token
            