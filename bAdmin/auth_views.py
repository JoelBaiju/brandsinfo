import json
import secrets
import string

# Django imports

from django.core.cache import cache
from django.shortcuts import get_object_or_404



# DRF imports
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from usershome.Tools_Utils.fast2_sms_service import send_otp
from rest_framework.decorators import api_view, permission_classes


# Local app imports

from django.contrib.auth import authenticate


@api_view(['POST'])  # Ensures this view works as an API view
def admin_auth_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON in request body'}, status=status.HTTP_400_BAD_REQUEST)
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Authentication successful',
            'sessionid': str(refresh.access_token),
            'refresh_token': str(refresh)
        }, status=status.HTTP_200_OK)
    
    return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
