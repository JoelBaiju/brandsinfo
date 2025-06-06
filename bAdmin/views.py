

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

from rest_framework.views import APIView

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
            'total_descriptive_cats': Buisness_Descriptive_cats.objects.count(),
            'total_general_cats':Buisness_General_cats.objects.count(),
            'buisness_signup_rates': buisness_signup_rates,
            }
        
        
        
        return Response({'data':data}, status=status.HTTP_200_OK)

    
    # else:
    #     return Response('You are not authorized to access this api', status=status.HTTP_403_FORBIDDEN)
    
    
    
    
    
    




# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from usershome.models import General_cats, Descriptive_cats
from .serializers import *



class AddGeneralCatsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        categories = request.data.get('gcats', [])
        created = []

        for cat in categories:
            obj, created_obj = General_cats.objects.get_or_create(cat_name=cat.strip())
            created.append(GeneralCatsSerializer(obj).data)

        return Response({'created': created}, status=status.HTTP_201_CREATED)



class AddDescriptiveCatsView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        general_cat_id = request.data.get('gid')
        descriptive_cats = request.data.get('dcats', [])

        if not general_cat_id or not descriptive_cats:
            return Response({'error': 'general_cat_id and categories are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            general_cat = General_cats.objects.get(id=general_cat_id)
        except General_cats.DoesNotExist:
            return Response({'error': 'General category not found'}, status=status.HTTP_404_NOT_FOUND)

        created = []
        for cat_name in descriptive_cats:
            obj, _ = Descriptive_cats.objects.get_or_create(
                cat_name=cat_name.strip(), general_cat=general_cat
            )
            created.append(DescriptiveCatsSerializer(obj).data)

        return Response({'created': created}, status=status.HTTP_201_CREATED)




from django.db.models import Count



from rest_framework.pagination import PageNumberPagination



class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page_size': self.get_page_size(self.request),
            'results': data
        })
        
        
class GetAllGcats(generics.ListAPIView):
    serializer_class = GeneralCatsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return General_cats.objects.annotate(
            dcats_count=Count('descriptive_cats')
        )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['total_dcat_count'] = Descriptive_cats.objects.count()
        response.data['total_gcat_count'] = General_cats.objects.count()
        return response



class GetAllDcats(generics.ListAPIView):
    serializer_class = DescriptiveCatsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        gid = self.request.GET.get('gid')
        if gid:
            return Descriptive_cats.objects.filter(general_cat=gid)
        return Descriptive_cats.objects.all()






class GetAllProductGeneralCats(generics.ListAPIView):
    serializer_class = ProductGeneralCatsSerializer
    pagination_class = CustomPagination
    
    
    def get_queryset(self):
        return Product_General_category.objects.annotate(
            dcats_count=Count('subcats')
        )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['total_dcat_count'] = Product_Sub_category.objects.count()
        response.data['total_gcat_count'] = Product_General_category.objects.count()
        return response



class GetAllProductSubCats(generics.ListAPIView):
    serializer_class = ProductSubCatsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        gid = self.request.GET.get('gid')
        if gid:
            return Product_Sub_category.objects.filter(general_cat_id=gid)
        return Product_Sub_category.objects.all()

    
    
    
    
    
import traceback

class EditGcats(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneralCatsSerializer
    queryset = General_cats.objects.all()
    
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()  # Prints full traceback in the console

            return Response(
                {"error": error_message}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
class EditDcats(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DescriptiveCatsSerializer
    queryset = Descriptive_cats.objects.all()
    
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()  # Prints full traceback in the console

            return Response(
                {"error": error_message}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    



class EditProductGcats(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductGeneralCatsSerializer
    queryset = Product_General_category.objects.all()
    
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()  # Prints full traceback in the console

            return Response(
                {"error": error_message}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
class EditProductSubcats(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSubCatsSerializer
    queryset = Product_Sub_category.objects.all()
    
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()  # Prints full traceback in the console

            return Response(
                {"error": error_message}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
            
            
            
@api_view(['POST'])
def get_dcat_with_id_single(request):
    id = request.GET.get('id')
    if not id:
        return Response({'detail': 'ID is required'}, status=400)
    try:
        obj = Descriptive_cats.objects.get(id=id)
    except Descriptive_cats.DoesNotExist:
        return Response({'detail': 'Descriptive category not found'}, status=404)
    
    return Response(DescriptiveCatsSerializer(obj).data)




            
@api_view(['POST'])
def get_gcat_with_id_single(request):
    id = request.GET.get('id')
    if not id:
        return Response({'detail': 'ID is required'}, status=400)
    try:
        obj = General_cats.objects.get(id=id)
    except General_cats.DoesNotExist:
        return Response({'detail': 'Descriptive category not found'}, status=404)
    
    return Response(GeneralCatsSerializer(obj).data)



class AddProductGeneralCatsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        categories = request.data.get('gcats', [])
        created = []

        for cat in categories:
            obj, created_obj = Product_General_category.objects.get_or_create(cat_name=cat.strip())
            created.append(ProductGeneralCatsSerializer(obj).data)

        return Response({'created': created}, status=status.HTTP_201_CREATED)




class AddProductSubCatsView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        general_cat_id = request.data.get('gid')
        descriptive_cats = request.data.get('dcats', [])

        if not general_cat_id or not descriptive_cats:
            return Response({'error': 'general_cat_id and categories are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            general_cat = Product_General_category.objects.get(id=general_cat_id)
        except General_cats.DoesNotExist:
            return Response({'error': 'General category not found'}, status=status.HTTP_404_NOT_FOUND)

        created = []
        for cat_name in descriptive_cats:
            obj, _ = Product_Sub_category.objects.get_or_create(
                cat_name=cat_name.strip(), general_cat=general_cat
            )
            created.append(ProductSubCatsSerializer(obj).data)

        return Response({'created': created}, status=status.HTTP_201_CREATED)










    
from usershome.serializers import BuisnessesSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def add_buisness_from_admin(request):
    if not request.user.is_superuser:
        return Response(
            {"detail": "You don't have the right privilege to access this API"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    print("Requesting admin user:", request.user)
    
    try:
        plan = Plans.objects.get(plan_name='Default Plan')  
    except Plans.DoesNotExist:
        return Response(
            {"detail": "Default Plan not found."},
            status=status.HTTP_400_BAD_REQUEST
        )

    request.data['user'] = request.data.get("uid")
    request.data['plan'] = plan.id  

    serializer = BuisnessesSerializer(data=request.data)
    print('Incoming data:', request.data)

    if serializer.is_valid():
        business = serializer.save(owner=request.user)
        business.plan = plan 
        business.save()

        return Response(
            BuisnessesSerializer(business).data,
            status=status.HTTP_201_CREATED
        )

    print('Validation errors:', serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






from usershome.Views.auth_views import create_new_user
from types import SimpleNamespace

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_users_from_admin(request):
    if not request.user.is_superuser:
        return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

    phone = request.data.get('phone')
    name = request.data.get('name')

    if not phone or not isinstance(phone, str) or len(phone) < 10:
        return Response({'error': 'Invalid or missing phone number.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not name or not isinstance(name, str):
        return Response({'error': 'Invalid or missing name.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        auth = SimpleNamespace(name=name)
        utype = 'buisness'
        user = create_new_user(phone, auth, utype)

        return Response({'detail': 'User created successfully.'}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': f'Failed to create user: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)














from usershome.serializers import UserSerializer


class get_users(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({'detail': 'You do not have permission to perform this action. //FCKOF//'}, status=status.HTTP_403_FORBIDDEN)
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):

        vendor = self.request.GET.get('vendor') == 'true'
        customer = self.request.GET.get('customer') == 'true'
        
        if vendor:
            users_queryset = Extended_User.objects.filter(is_vendor=True)
        elif customer :
            users_queryset = Extended_User.objects.filter(is_customer=True)
        else:
            users_queryset = Extended_User.objects.all()

        return users_queryset
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['total_user_count'] = Extended_User.objects.count()
        response.data['total_vendors_count'] = Extended_User.objects.filter(is_vendor =True).count()
        response.data['total_customer_count'] = Extended_User.objects.filter(is_customer =True).count()
        return response




class get_buisnesses(generics.ListAPIView):
    serializer_class = BuisnessesAdminlistSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return Buisnesses.objects.all()
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['total_buisness_count'] = Buisnesses.objects.count()
        response.data['total_product_buisness_count'] = Buisnesses.objects.filter(buisness_type='Product').count()
        response.data['total_service_buisness_count'] = Buisnesses.objects.filter(buisness_type='Service').count()
        response.data['total_hybrid_buisness_count'] = Buisnesses.objects.filter(buisness_type='Products & Services').count()
        return response


