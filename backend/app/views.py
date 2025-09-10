import json
import jwt
import time
import requests
import logging

from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_connection_token(request):

    token_claims = {
        'sub': str(request.user.pk),
        'exp': int(time.time()) + 120
    }
    token = jwt.encode(token_claims, settings.CENTRIFUGO_TOKEN_SECRET)
    return Response({'token': token})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_token(request):
    channel = request.query_params.get('channel')
    if channel != f'personal:{request.user.pk}':
        return Response({'detail': 'permission denied'}, status=403)

    token_claims = {
        'sub': str(request.user.pk),
        'exp': int(time.time()) + 300,
        'channel': channel
    }
    token = jwt.encode(token_claims, settings.CENTRIFUGO_TOKEN_SECRET)
    return Response({'token': token})
