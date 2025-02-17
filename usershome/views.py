import json
from django.shortcuts import render
from .models import Products, catalogue
from django.http import HttpResponse
from .searcher import find_closest
from django.core.exceptions import ObjectDoesNotExist



import secrets
import string


from django.core.cache import cache

from rest_framework import generics, filters

from rest_framework.decorators import api_view

from rest_framework.generics import GenericAPIView
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken


from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
    


class BuisnessesView(generics.ListAPIView):
    queryset = Buisnesses.objects.all()
    serializer_class = BuisnessesSerializer

    def get_queryset(self):
        # Optionally, filter the queryset if you want to return businesses associated with the user
        if self.request.user.is_authenticated:
            print(self.request.user)
            user = Extended_User.objects.get(username=self.request.user)
            return [Buisnesses.objects.filter(user=user) , user]
        return Buisnesses.objects.none()

    def get(self , request):
        if self.request.user.is_authenticated:
            qset = self.get_queryset()
            buisnesses = BuisnessesSerializer(qset[0] , many=True).data
            user = UserSerializer(qset[1]).data
            # print(qset[1].name)
            return Response({"userprofile":user,'buisnesses':buisnesses},status=status.HTTP_200_OK)
        return Response('Authentication required' , status=status.HTTP_401_UNAUTHORIZED)
    
    
    
    def post(self, request):
        request.data['user']=Extended_User.objects.get(username=request.user).id
        print(request.data)
        if request.user.is_anonymous:
            return Response(
                {"detail": "Authentication required to create a business."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            business = serializer.save(owner=request.user)
            return Response(
                self.serializer_class(business).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
   
    
    

@api_view(['GET'])
def get_locality_with_city(request):
    city_name = request.GET.get('city', '').strip()
    if not city_name:
        return Response({'error': 'Query parameter "city" is required'}, status=400)
    
    try:
        city = City.objects.get(city_name=city_name)
    except ObjectDoesNotExist:
        return Response({'error': 'City not found'}, status=404)
    
    localities = Locality.objects.filter(city=city)
    serialized = LocalitySerializer(localities, many=True)
    
    return Response({'data':serialized.data,"city":city.id } )






def generate_random_otp(length=6):
    otp=''.join(secrets.choice(string.digits) for _ in range(length))
    print(otp)
    return otp






@api_view(['POST'])
def signup_request_1(request):
    try:
        data = json.loads(request.body)
        phone = data.get('phone')

        if not phone:
            return Response({'message': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        exists = Extended_User.objects.filter(username=phone).exists()
        
        # Generate OTP
        otp = generate_random_otp()
        
        # Store OTP and phone number in cache with timeout (10 minutes)
        cache.set(
            f'otp_{phone}',
            value={'otp': otp, 'phone': phone, 'exists': exists , 'name':'' },
            timeout=600  # Timeout in seconds (10 minutes)
        )
        
        return Response({'exists': exists,'otp':otp},status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({'success': False, 'message': 'Invalid JSON format.'}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        # Log or print error for debugging purposes
        print(f"Error in signup_request_1: {str(e)}")
        return Response({'success': False, 'message': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








@api_view(['POST'])
def verifyotp(request):
    data = json.loads(request.body)
    phone=data.get('phone')
    otp=data.get('otp')
    

    cache_data=cache.get(f'otp_{phone}')
    if cache_data == None:
         return Response({'message':'OTP Expired',
                         'exists':cache_data['exists'],},
                        status=status.HTTP_400_BAD_REQUEST)
         
    print(cache_data)
    if otp==cache_data['otp']:
        print('done otp verified')
        if cache_data['exists']:
            user=Extended_User.objects.get(username=cache_data['phone'])
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)      
            print(access_token)
            return Response({'message':'OTP Verified',
                             'exists':cache_data['exists'],
                             'sessionid':access_token,
                             'refresh_token':str(refresh)},
                            status=status.HTTP_201_CREATED
                            )
        else:
            
            UserObj=Extended_User.objects.create_user(
                username=phone, 
                password=phone+cache_data['name'],  
                mobile_number=phone,
                first_name=cache_data['name']
            )
            UserObj.save()
            refresh = RefreshToken.for_user(UserObj)
            access_token = str(refresh.access_token)
            
            return Response({'message':'OTP Verified',
                             'exists':cache_data['exists'], 
                            'sessionid':access_token,
                             'refresh_token':str(refresh)},   
                            status=status.HTTP_201_CREATED
                            )
            
    else:
        print('Invalid OTP')
        return Response({'message':'Invalid OTP',
                         'exists':cache_data['exists'],},
                        status=status.HTTP_400_BAD_REQUEST)

    
    




@api_view(['POST'])    
def signup_request_2(request):
    
    data=json.loads(request.body)
    phone=data.get('phone')
    name=data.get('name')
    cache_data=cache.get(f'otp_{phone}')
    try:
        cache.set(f'otp_{phone}', value={
                                    'otp': cache_data['otp'],
                                    'name': name,
                                    'exists': cache_data['exists'],
                                    'phone':phone
                                    }, timeout=600) 
        return Response({
                     'message':'Name Saved',
                    } ,status=status.HTTP_200_OK)  
    except:
        return Response({
                     'message':'Something Went Wrong',
                    } ,status=status.HTTP_400_BAD_REQUEST)  

  
    
     



@api_view(['POST'])
def resendotp(request):
    data=json.loads(request.body)
    phone=data.get('phone')
    cache_data=cache.get(f'otp_{phone}')   
    otp=generate_random_otp()
    cache.set(f'otp_{phone}', value={
                                    'otp': otp,
                                    'phone': phone,
                                    'exists': cache_data['exists'],
                                    'name':cache_data['name']
                                    }, timeout=600) 
    print(otp)
                                    
    return Response({'message':'Otp sent sucessfully'},status=status.HTTP_200_OK)
    
    
    
    
# =================================================================================================================




@api_view(['GET'])
def search_products_category(request):
    query = request.GET.get('q', '')
    if not query:
        return Response({'error': 'Query parameter "q" is required'}, status=400)

    cats = find_closest('usershome_product_sub_category',query)
    return Response(cats)


from rest_framework.parsers import MultiPartParser, FormParser 


class AddProductWithImagesView(generics.CreateAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
     
    def create(self, request, *args, **kwargs):
        print(request.data)
        # data = request.data.copy()
        
        # images = request.FILES.getlist('images[]')
        data = request.data
        images = request.FILES.getlist('images[]')  

        data.setlist('images', images)  # Ensure images are properly set as a list

        serializer = self.get_serializer(data=data)
        
        if serializer.is_valid():
            product = serializer.save()
            return Response({'buisness_type':Buisnesses.objects.get(id=data.get('buisness')).buisness_type}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    




class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Services.objects.all()
    serializer_class = ServiceSerializer
    parser_classes = [MultiPartParser, FormParser]  # Allows image uploads
    filter_backends = [filters.SearchFilter]  
    search_fields = ['buisness']  # Enables filtering by business ID

    def post(self, request, *args, **kwargs):
        print(request.POST)
        return super().post(request, *args, **kwargs)

    
    
    
    
class ServiceCats(generics.ListCreateAPIView):
    queryset = Service_Cats.objects.all()
    serializer_class = ServiceCatsSerializer
        
    
    
    
    
    
    
    
# def create_descriptive_cats(bid):
    
#     buisness=Buisnesses.objects.get(id=bid)
#     products = Products.objects.filter(buisness=buisness)
    
#     print(buisness.buisness_type)
#     print(products[0].name)

#     for i in products:
#         print(i.name) 
#         if buisness.buisness_type == 'product'   :
#             print(i.name+' '+'Dealer')
        

    
    


@api_view(['GET'])
def search_general_category(request):
    query = request.GET.get('q', '')
    if not query:
        return Response({'error': 'Query parameter "q" is required'}, status=400)

    cats = find_closest('usershome_general_cats',query)
    return Response(cats)



@api_view(['POST'])
def add_bg_category(request):
    data=json.loads(request.body)
    cid=data.get('cid')
    bid=data.get('bid')
    print(cid,bid)
    if not cid or not bid:
        return Response('',status=status.HTTP_400_BAD_REQUEST)
    
    Buisness_General_cats.objects.create(gcat=General_cats.objects.get(id=cid) , buisness=Buisnesses.objects.get(id=bid)).save()
    
    return Response('',status=status.HTTP_200_OK)







@api_view(['GET'])
def get_des_category(request):
    gcid = request.GET.get('gcid', '')
    if not gcid:
        return Response({'error': 'Query parameter "gcid" is required'}, status=400)

    try:
        general_cat = General_cats.objects.get(id=gcid)  # Fetch the general category
    except General_cats.DoesNotExist:
        return Response({'error': 'General category not found'}, status=404)

    cats = Descriptive_cats.objects.filter(general_cat=general_cat)
    
    serialized = DescriptiveCatsSerializer(cats, many=True)
    
    return Response(serialized.data)

@api_view(['POST'])
def add_des_category(request):
    data=json.loads(request.body)
    dcid=data.get('dcid')
    bid=data.get('bid')
    if not dcid or not bid:
        return Response('',status=status.HTTP_400_BAD_REQUEST)
    for i in dcid:
        Buisness_Descriptive_cats.objects.create(dcat=Descriptive_cats.objects.get(id=i) , buisness=Buisnesses.objects.get(id=bid)).save()
    
    return Response('',status=status.HTTP_200_OK)

    
    

@api_view(['GET'])
def search(request):
    query = request.GET.get('q','')
    print(query)
    
    return Response('ihb')