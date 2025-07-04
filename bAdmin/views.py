

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


@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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












from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from usershome.models import City, Locality
from .serializers import CitySerializer, LocalitySerializer


class AddCities(APIView):
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def post(self, request):
        city_list = request.data  # ["CITY1", "CITY2", ...]
        created = []

        for city_name in city_list:
            city, is_created = City.objects.get_or_create(city_name=city_name.strip())
            if is_created:
                created.append(city)

        serializer = CitySerializer(created, many=True)
        return Response({"added_cities": serializer.data}, status=status.HTTP_201_CREATED)

    def get(self, request):
        cities = City.objects.all()
        paginator = self.pagination_class()
        paginated_qs = paginator.paginate_queryset(cities, request)
        serializer = CitySerializer(paginated_qs, many=True)

        total_city_count = cities.count()
        total_locality_count = Locality.objects.count()

        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data["total_city_count"] = total_city_count
        paginated_response.data["total_locality_count"] = total_locality_count

        return paginated_response


class AddLocalities(APIView):
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data  # [{"CITY": 1, "LOCAITY": "LOCALITY1"}, ...]
        created = []
        errors = []
        
        localities = data.get("LOCAITY")
        city_id = data.get("CITY")
        city = City.objects.get(id=city_id)

        for locality in localities:
            try:
                locality_name = locality

                if not city_id or not locality_name:
                    raise ValueError("Missing CITY or LOCAITY")

                locality, is_created = Locality.objects.get_or_create(
                    city=city,
                    locality_name=locality_name.strip()
                )
                if is_created:
                    created.append(locality)
            except Exception as e:
                errors.append({"data": locality, "error": str(e)})

        serializer = LocalitySerializer(created, many=True)
        return Response({
            "added_localities": serializer.data,
            "errors": errors
        }, status=status.HTTP_201_CREATED)


    def get(self, request):
        city_id = request.query_params.get('cid')       

        if city_id:
            localities = Locality.objects.select_related('city').filter(city__id=city_id)
        else:
            localities = Locality.objects.select_related('city').all()

        paginator = self.pagination_class()
        paginated_qs = paginator.paginate_queryset(localities, request)
        serializer = LocalitySerializer(paginated_qs, many=True)

        total_city_count = City.objects.count()
        total_locality_count = Locality.objects.count()

        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data["total_city_count"] = total_city_count
        paginated_response.data["total_locality_count"] = total_locality_count

        return paginated_response




from rest_framework.generics import UpdateAPIView, DestroyAPIView


# --- Cities ---

class EditCityAPIView(UpdateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]


class DeleteCityAPIView(DestroyAPIView):
    queryset = City.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]


# --- Localities ---

class EditLocalityAPIView(UpdateAPIView):
    queryset = Locality.objects.all()
    serializer_class = LocalitySerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]


class DeleteLocalityAPIView(DestroyAPIView):
    queryset = Locality.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]











from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from usershome.models import Buisnesses, Buisness_keywords, Keywords, General_cats, Descriptive_cats, Buisness_General_cats, Buisness_Descriptive_cats

def browse_businesses(request):
    search_query = request.GET.get('search', '')
    
    # Get all businesses or filtered by search
    if search_query:
        businesses = Buisnesses.objects.filter(
            Q(name__icontains=search_query) |
            Q(buisness_type__icontains=search_query) |
            Q(description__icontains=search_query)
        ).order_by('name')
        
        # If exactly one match, redirect to that business
        if businesses.count() == 1:
            return redirect(f"{request.path}?page={businesses[0].id}")
    else:
        businesses = Buisnesses.objects.all().order_by('name')
    
    # Pagination - 1 business per page
    paginator = Paginator(businesses, 1)
    page_number = request.GET.get('page')
    
    # Handle direct business ID viewing
    if page_number and page_number.isdigit():
        try:
            business = Buisnesses.objects.get(id=int(page_number))
            businesses = Buisnesses.objects.filter(id=business.id)
            paginator = Paginator(businesses, 1)
        except Buisnesses.DoesNotExist:
            pass
    
    page_obj = paginator.get_page(page_number)
    current_business = page_obj.object_list[0] if page_obj.object_list else None
    
    # Get related data for current business
    keywords = None
    general_categories = None
    descriptive_categories = None
    all_general_cats = General_cats.objects.all()
    all_descriptive_cats = Descriptive_cats.objects.all()
    
    if current_business:
        keywords = Buisness_keywords.objects.filter(buisness=current_business)
        general_categories = Buisness_General_cats.objects.filter(buisness=current_business)
        descriptive_categories = Buisness_Descriptive_cats.objects.filter(buisness=current_business)
    
    # Handle all operations
    if request.method == 'POST':
        # Delete keyword
        if 'delete_keyword' in request.POST:
            keyword_id = request.POST.get('keyword_id')
            keyword_to_delete = get_object_or_404(Buisness_keywords, id=keyword_id)
            keyword_to_delete.delete()
        
        # Add new keyword
        elif 'add_keyword' in request.POST:
            keyword_text = request.POST.get('new_keyword', '').strip()
            if keyword_text and current_business:
                keyword, created = Keywords.objects.get_or_create(keyword=keyword_text.lower())
                Buisness_keywords.objects.get_or_create(keyword=keyword, buisness=current_business)
        
        # Add general category
        elif 'add_general_cat' in request.POST:
            general_cat_id = request.POST.get('general_cat_id')
            if general_cat_id and current_business:
                general_cat = get_object_or_404(General_cats, id=general_cat_id)
                Buisness_General_cats.objects.get_or_create(gcat=general_cat, buisness=current_business)
        
        # Delete general category
        elif 'delete_general_cat' in request.POST:
            general_cat_id = request.POST.get('general_cat_id')
            if general_cat_id and current_business:
                Buisness_General_cats.objects.filter(
                    gcat_id=general_cat_id,
                    buisness=current_business
                ).delete()
        
        # Add descriptive category
        elif 'add_descriptive_cat' in request.POST:
            descriptive_cat_id = request.POST.get('descriptive_cat_id')
            if descriptive_cat_id and current_business:
                descriptive_cat = get_object_or_404(Descriptive_cats, id=descriptive_cat_id)
                Buisness_Descriptive_cats.objects.get_or_create(
                    dcat=descriptive_cat,
                    buisness=current_business
                )
        
        # Delete descriptive category
        elif 'delete_descriptive_cat' in request.POST:
            descriptive_cat_id = request.POST.get('descriptive_cat_id')
            if descriptive_cat_id and current_business:
                Buisness_Descriptive_cats.objects.filter(
                    dcat_id=descriptive_cat_id,
                    buisness=current_business
                ).delete()
        
        return redirect(request.path + f'?page={page_number}')
    
    context = {
        'page_obj': page_obj,
        'current_business': current_business,
        'keywords': keywords,
        'search_query': search_query,
        'general_categories': general_categories,
        'descriptive_categories': descriptive_categories,
        'all_general_cats': all_general_cats,
        'all_descriptive_cats': all_descriptive_cats,
    }
    
    return render(request, 'browse_businesses.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
import json
from usershome.serializers import BuisnessesSerializerMini

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def business_tune_api(request):
    response_data = {'status': 'success', 'data': {}}
    
    try:
        # Handle GET requests (search/fetch)
        if request.method == 'GET':
            search_query = request.GET.get('search', '').strip()
            business_id = request.GET.get('bid', '').strip()
            
            # Build query filters
            filters = Q()
            if search_query:
                filters &= (
                    Q(name__icontains=search_query) |
                    Q(buisness_type__icontains=search_query) |
                    Q(description__icontains=search_query)
                )
            
            if business_id:
                filters &= Q(id=business_id)
            
            # Get filtered businesses
            biz = Buisnesses.objects.filter(filters).order_by('name').first()
            # Serialize businesses
            response_data['data']['businesses'] = [
                {
                    'id': biz.id,
                    'name': biz.name,
                    'qa_passed':biz.qa_passed,
                    'profile_pic':  BuisnessesSerializerMini(biz).data.get('image'),
                    'building_name':biz.building_name,
                    'business_type': biz.buisness_type,
                    'description': biz.description,
                    'keywords': list(Buisness_keywords.objects.filter(buisness=biz)
                                   .values('keyword__keyword', 'id')),
                    'general_categories': list(Buisness_General_cats.objects.filter(buisness=biz)
                                               .values('gcat__cat_name', 'gcat__id')),
                    'descriptive_categories': list(Buisness_Descriptive_cats.objects.filter(buisness=biz)
                                            .values('dcat__cat_name', 'dcat__id')),
                }
            ]
        
        # Handle POST requests (edits)
        elif request.method == 'POST':
            try:
                data = json.loads(request.body)
                business_id = data.get('bid')
                action = data.get('action')
                
                if not business_id:
                    raise ValueError("Business ID is required")
                
                business = Buisnesses.objects.get(id=business_id)
                print(action, data.get('cid'))
                # Handle different actions
                if action == 'delete_keyword':
                    keyword_id = data.get('keyword_id')
                    keyword_to_delete = get_object_or_404(Buisness_keywords, id=keyword_id)
                    keyword_to_delete.delete()
                    response_data['message'] = 'Keyword deleted successfully'
                
                elif action == 'add_keyword':
                    keyword_text = data.get('keyword', '').strip()
                    if keyword_text:
                        keyword, created = Keywords.objects.get_or_create(keyword=keyword_text.lower())
                        Buisness_keywords.objects.get_or_create(keyword=keyword, buisness=business)
                        response_data['message'] = 'Keyword added successfully'
                
                elif action == 'add_general_cat':
                    cat_id = data.get('cid')
                    if cat_id:
                        cat = get_object_or_404(General_cats, id=cat_id)
                        Buisness_General_cats.objects.get_or_create(gcat=cat, buisness=business)
                        response_data['message'] = 'General category added successfully'
                
                elif action == 'delete_general_cat':
                
                    cat_id = data.get('cid')
                    if cat_id:  
                        Buisness_General_cats.objects.filter(gcat_id=cat_id, buisness=business).delete()
                        print('delete general cat', cat_id)
                        response_data['message'] = 'General category deleted successfully'
                
                elif action == 'add_descriptive_cat':
                    cat_id = data.get('cid')
                    if cat_id:
                        for i in cat_id:
                            cat = get_object_or_404(Descriptive_cats, id=i)
                            Buisness_Descriptive_cats.objects.get_or_create(dcat=cat, buisness=business)
                        response_data['message'] = 'Descriptive category added successfully'
                
                elif action == 'delete_descriptive_cat':
                    cat_id = data.get('cid')
                    if cat_id:
                        Buisness_Descriptive_cats.objects.filter(dcat_id=cat_id, buisness=business).delete()
                        response_data['message'] = 'Descriptive category deleted successfully'
                
                elif action == 'pass_qa':
                    if business:
                        business.qa_passed=True
                        business.save()
                        response_data['message'] = 'QA Check Updated Successfully'
                

                else:
                    response_data['status'] = 'error'
                    response_data['message'] = 'Invalid action specified'
                
                # Return updated business data
                response_data['data'] = {
                    'keywords': list(Buisness_keywords.objects.filter(buisness=business)
                               .values_list('keyword__keyword', flat=True)),
                    'general_categories': list(Buisness_General_cats.objects.filter(buisness=business)
                                        .values_list('gcat__cat_name', flat=True)),
                    'descriptive_categories': list(Buisness_Descriptive_cats.objects.filter(buisness=business)
                                                .values_list('dcat__cat_name', flat=True)),
                }
            
            except json.JSONDecodeError:
                response_data = {'status': 'error', 'message': 'Invalid JSON data'}
            except Buisnesses.DoesNotExist:
                response_data = {'status': 'error', 'message': 'Business not found'}
            except Exception as e:
                response_data = {'status': 'error', 'message': str(e)}
    
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
    
    return JsonResponse(response_data)



@api_view(['GET'])
def business_search_view(request):
    """
    Renders the business search page that connects to the Elasticsearch API
    """
    # You can pass any initial data needed by the template here
    context = {
        'api_endpoint': '/users/esearch/',  # Your API endpoint
        'default_location': 'New Delhi',    # Default location if needed
    }
    return render(request, 'search_page.html', context)







from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import re

from usershome.models import Buisnesses, Plans, Plan_Varients


def parse_duration(duration_val):
    """Parses duration as int (days) or strings like '30 days', '6 months', '1 year' into timedelta."""
    if isinstance(duration_val, int):
        return timedelta(days=duration_val)
    if isinstance(duration_val, str):
        duration_str = duration_val.lower().strip()
        if duration_str.isdigit():
            return timedelta(days=int(duration_str))
        if "day" in duration_str:
            days = int(re.findall(r'\d+', duration_str)[0])
            return timedelta(days=days)
        elif "month" in duration_str:
            months = int(re.findall(r'\d+', duration_str)[0])
            return timedelta(days=30 * months)
        elif "year" in duration_str:
            years = int(re.findall(r'\d+', duration_str)[0])
            return timedelta(days=365 * years)
    return timedelta(days=30)  # Default fallback


from communications.draft4sms import send_plan_purchased_draft4sms


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_plan_to_buisness(request):
    try:
        buisness_id = request.data.get("business_id")
        plan_id = request.data.get("plan_id")
        variant_id = request.data.get("variant_id")
        print(buisness_id,plan_id,variant_id)
        if not buisness_id or not plan_id or not variant_id:
            return Response({"error": "buisness_id, plan_id, and variant_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            buisness = Buisnesses.objects.get(id=buisness_id)
        except Buisnesses.DoesNotExist:
            return Response({"error": "Buisness not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            plan = Plans.objects.get(id=plan_id)
        except Plans.DoesNotExist:
            return Response({"error": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            variant = Plan_Varients.objects.get(id=variant_id, plan=plan)
        except Plan_Varients.DoesNotExist:
            return Response({"error": "Plan variant not found or does not belong to the selected plan."}, status=status.HTTP_404_NOT_FOUND)

        # Calculate dates
        start_date = datetime.today().date()
        expiry_date = start_date + parse_duration(variant.duration)
        print(expiry_date)
        print(variant.duration)
        print(start_date)

        # Set fields
        buisness.plan = plan
        buisness.plan_variant = variant
        buisness.plan_start_date = start_date
        buisness.plan_expiry_date = expiry_date

        # Optionally adjust search priority based on plan
        if plan.search_priority_3:
            buisness.search_priority = 3
        elif plan.search_priority_2:
            buisness.search_priority = 2
        elif plan.search_priority_1:
            buisness.search_priority = 1
        else:
            buisness.search_priority = 0
 
        if plan.bi_assured:
            buisness.assured = True
        if plan.bi_verification:
            buisness.verified = True

        buisness.save()
        AdminDirectTransactions.objects.create(user= buisness.user,
                                               buisness=buisness,
                                               amount = variant.price,
                                               plan = plan,
                                               plan_variant= variant,
                                               payment_mode= 'Handled by admin'
                                               )
        send_plan_purchased_draft4sms(buisness.name,plan.verbouse_name, expiry_date, buisness.user.username)
        return Response({
            "message": "Plan successfully added to the business.",
            "buisness_id": buisness.id,
            "plan": plan.plan_name,
            "variant": variant.duration,
            "plan_start_date": str(start_date),
            "plan_expiry_date": str(expiry_date),
            "search_priority": buisness.search_priority
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['GET'])
def add_location(request):
    # if request is None:
    #     return render(request,'addlocation.html',{'bid':bid})
    lon = request.GET.get('lon')
    lat = request.GET.get('lat')
    bid = request.GET.get('bid')
    
    print(lon,lat,bid)
   
    if lon and lat and bid:
        buisness = Buisnesses.objects.get(id=int(float(bid)))
        if buisness.latittude == None and buisness.longitude == None or buisness.latittude == '' and buisness.longitude == '':
            buisness.latittude = lat
            buisness.longitude = lon
            print("from buisness",buisness.latittude,buisness.longitude)
            buisness.save()
            print('Added your location')
            return Response('Added your location')
    
        else :
            print('Location already added')
            return Response('Location already added')
    if request.method == 'GET':
        return render(request , 'addlocation.html',{'bid':bid,})
    
    