import jwt
from django.conf import settings
from rest_framework.permissions import BasePermission


class IsServiceToken(BasePermission):
    """
    Allows access only to service-to-service calls identified by JWT claims.
    Accepts either:
      - claim "role" == "service"
      - or claim "scp" (scope) containing "chat.manage"
    """

    def has_permission(self, request, view):
        raw = request.auth
        if not raw:
            return False
        try:
            payload = jwt.decode(raw, settings.JWT_SECRET, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return False
        if payload.get('role') == 'service':
            return True
        scopes = payload.get('scp') or payload.get('scope')
        if isinstance(scopes, str):
            scopes = scopes.split()
        return isinstance(scopes, (list, tuple)) and 'chat.manage' in scopes

