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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def device_register_view(request):
    device_info = request.data.get('device')
    if not device_info:
        return Response({'detail': 'device not found'}, status=400)

    # Attach user ID to device info.
    device_info["user"] = str(request.user.pk)

    session = requests.Session()
    try:
        resp = session.post(
            settings.CENTRIFUGO_HTTP_API_ENDPOINT + '/api/device_register',
            data=json.dumps(device_info),
            headers={
                'Content-type': 'application/json',
                'X-API-Key': settings.CENTRIFUGO_HTTP_API_KEY,
                'X-Centrifugo-Error-Mode': 'transport'
            }
        )
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return Response({'detail': 'failed to register device'}, status=500)

    if resp.status_code != 200:
        logging.error(resp.json())
        return Response({'detail': 'failed to register device'}, status=500)

    return Response({'device_id': resp.json().get('result', {}).get('id')})
