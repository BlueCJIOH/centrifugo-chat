import jwt
from dataclasses import dataclass
from django.conf import settings
from rest_framework import authentication, exceptions


@dataclass
class JWTUser:
    id: str

    @property
    def pk(self):
        return self.id

    @property
    def is_authenticated(self):
        return True


class JWTAuthentication(authentication.BaseAuthentication):
    """Authenticate requests using a JWT issued by the main service."""
    keyword = 'Bearer'

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).decode('utf-8')
        if not auth or not auth.startswith(self.keyword + ' '):
            return None
        token = auth.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        # TODO: call external service /auth/verify to ensure token is still valid.
        user_id = payload.get('sub')
        if not user_id:
            raise exceptions.AuthenticationFailed('Missing sub claim')
        return JWTUser(id=str(user_id)), token
