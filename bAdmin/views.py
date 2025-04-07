

import json
import secrets
import string

# Django imports

from django.core.cache import cache
from django.shortcuts import get_object_or_404



# DRF imports
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from usershome.Tools_Utils.fast2_sms_service import send_otp


# Local app imports

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from usershome.models import *


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Add_plan (request):
    data        = json.loads(request.body)
    plan_name   = data.get('plan_name')
    bid         = data.get('bid')
    buisnesss        = Buisnesses.objects.get(id = bid)
    try:
        plan                = Plans.objects.get(plan_name = plan_name)
        buisnesss.plan      = plan
        if plan.search_priority_1:
            buisnesss.search_priority  = 1 
        elif plan.search_priority_2:
            buisnesss.search_priority  = 2
        elif plan.search_priority_3:
            buisnesss.search_priority  = 3
            
    except:
        return Response('Invalid plan',status=status.HTTP_400_BAD_REQUEST)        
    return Response('Plan added successfully')



