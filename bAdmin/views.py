

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
from rest_framework.permissions import IsAuthenticated , IsAdminUser
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





from django.db.models import Count


# @permission_classes([IsAuthenticated])
@api_view(['GET'])
def admin_dashboard_view(request):
    # if  request.user.is_superuser:
        
        with_buisness = Extended_User.objects.annotate(num_businesses=Count('buisnesses')).filter(num_businesses__gt=0).count()
        total_users = Extended_User.objects.count()
        
        buisness_signup_rates = Buisnesses.objects.values('created_on__day').annotate(count=Count('id')).order_by('created_on__day')
        
        data = {
            'total_users'       : total_users,
            'user_distribution' : {
                'with_buisness_percentage' : round((with_buisness / total_users) * 100 if total_users > 0 else 0),
                'without_buisness_percentage': round(((total_users - with_buisness) / total_users) * 100 if total_users > 0 else 0),
                'with_buisness'     : with_buisness, 
                'without_buisness'  : total_users - with_buisness,
            },  
            
            'total_buisnesses'  : Buisnesses.objects.count(),
            'tier_1_subs'       : Buisnesses.objects.filter(plan=Plans.objects.get(plan_name='Tier 1')).count(),
            'tier_2_subs'       : Buisnesses.objects.filter(plan=Plans.objects.get(plan_name='Tier 2')).count(),
            'tier_3_subs'       : Buisnesses.objects.filter(plan=Plans.objects.get(plan_name='Tier 3')).count(),
            'no_plan'           : Buisnesses.objects.filter(plan=Plans.objects.get(plan_name='Default Plan')).count(),
            'total_products'    : Products.objects.count(),
            'total_services'    : Services.objects.count(),
            
            'service_bs' : {
                            'count'     :Buisnesses.objects.filter(buisness_type='Service').count(),
                            'percentage':round((Buisnesses.objects.filter(buisness_type='Service').count()/Buisnesses.objects.count())*100),
            },
            'product_bs' : {
                            'count'     :Buisnesses.objects.filter(buisness_type='Product').count(),
                            'percentage':round((Buisnesses.objects.filter(buisness_type='Product').count()/Buisnesses.objects.count())*100),
            },       
            'hybrid_bs' : {
                            'count'     :Buisnesses.objects.filter(buisness_type='Products & Services').count(),
                            'percentage':round((Buisnesses.objects.filter(buisness_type='Products & Services').count()/Buisnesses.objects.count())*100.),
            },

            'total_products': Products.objects.count(),
            'total_services': Services.objects.count(),
            
            'buisness_signup_rates': buisness_signup_rates,
            }
        
        
        
        return Response({'data':data}, status=status.HTTP_200_OK)

    
    # else:
    #     return Response('You are not authorized to access this api', status=status.HTTP_403_FORBIDDEN)