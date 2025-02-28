import json
import secrets
import string

# Django imports
from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict


# DRF imports
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser 
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


# Local app imports
from .models import *
from .serializers import * 
from .searcher import find_closest 

# E searcher imports
from elasticsearch_dsl import Q
from .e_searcher import *
from elasticsearch_dsl import Search




def count_filled_fields(instance):
    data_dict = model_to_dict(instance, exclude=["id","score"," no_of_views" , "no_of_enquiries" ,"sa_rate","user","latittude"]) 
    filled_fields = {key: value for key, value in data_dict.items() if value not in [None, "", [], {}]}
    print(filled_fields)
    return len(filled_fields)



def BuisnessScore(buisness):
    fieldcount=count_filled_fields(buisness)
    score_in_percentage=(fieldcount/21)*100
    return (int(score_in_percentage))

class BuisnessesView(generics.ListAPIView):
    queryset = Buisnesses.objects.all()
    serializer_class = BuisnessesSerializer

    def get_queryset(self):
        # Optionally, filter the queryset if you want to return businesses associated with the user
        if self.request.user.is_authenticated:
            print(self.request.user)
            try:
                user = Extended_User.objects.get(username=self.request.user)
                print('userrrrrrrrrrrrrrrr',user)
            except: 
                return Response('User not found')
            buisness=[Buisnesses.objects.filter(user=user) , user]
            print(buisness)
            return buisness
        return Buisnesses.objects.none()
    

    def get(self , request):
        if self.request.user.is_authenticated:
            bid=request.GET.get('bid')
            if bid:
                print('hrrrrr',bid)
                try:
                    buisness = Buisnesses.objects.get(id=bid)
                    buisness.score=BuisnessScore(buisness)
                    buisness.save()
                    user = Extended_User.objects.get(username=self.request.user)


                    if buisness.buisness_type == 'service':
                        services = Services.objects.filter(buisness=buisness)
                        
                        return Response(    
                                            {   
                                                'buisness':BuisnessesSerializerFull(buisness).data,
                                                'services':ServiceSerializer(services , many=True).data,
                                                'analytics':{
                                                                'average_time_spend':'0',
                                                                'keywords':['hospital','workshop','restaurant']                                                            
                                                            },
                                                'products':[],
                                                'user': UserSerializer(user).data
                                            },
                                            status=status.HTTP_200_OK
                                        )
                    elif buisness.buisness_type == 'product':
                        products = Products.objects.filter(buisness=buisness)
                        
                        
                        return Response(    
                                            {   
                                                'buisness':BuisnessesSerializerFull(buisness).data,
                                                'products':ProductSerializer(products , many=True).data,
                                                'analytics':{
                                                                'average_time_spend':'0',
                                                                'keywords':['hotel','bank','store']
                                                            }, 
                                                'services':[],
                                                'user': UserSerializer(user).data

                                            },
                                            status=status.HTTP_200_OK
                                        )
                    else :
                        
                        print(buisness)
                        products = Products.objects.filter(buisness=buisness)
                        services = Services.objects.filter(buisness=buisness)
                        print (products,services)
                        return Response(    
                                            {   
                                                'buisness':BuisnessesSerializerFull(buisness).data,
                                                'services':ServiceSerializer(services , many=True).data,
                                                'analytics':{
                                                                'average_time_spend':'0',
                                                                'keywords':['hospital','workshop','restaurant']                                                            
                                                            },
                                                'products':ProductSerializer(products , many=True).data,
                                                'user': UserSerializer(user).data
                                            },
                                            status=status.HTTP_200_OK
                                        )

                        
                except:
                    return Response('No Buisnesess Found',status=status.HTTP_400_BAD_REQUEST)

            else:
                qset = self.get_queryset()
                try:
                    buisnesses = BuisnessesSerializerMini(qset[0] , many=True).data
                except:
                    return Response('No Buisnesess Found',status=status.HTTP_400_BAD_REQUEST)
                
                user = UserSerializer(qset[1]).data
                return Response({"userprofile":user,'buisnesses':buisnesses},status=status.HTTP_200_OK)
        
        return Response('Authentication required' , status=status.HTTP_401_UNAUTHORIZED)
    
    
    
    
    
    def post(self, request):
        print(request.data) 
        if request.user.is_anonymous:
            return Response(
                {"detail": "Authentication required to create a business."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        print(request.user)
        request.data['user'] = Extended_User.objects.get(username = request.user).id

        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            business = serializer.save(owner = request.user)
            return Response(
                self.serializer_class(business).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
   
    
    
    
    
def tracker_addtime(self , request):
    
    return Response(status=status.HTTP_200_OK)


class BuisnessesEdit(generics.UpdateAPIView):
    queryset = Buisnesses.objects.all()
    serializer_class = BuisnessesSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    

class BuisnessesView_for_customers(generics.ListAPIView):
    queryset = Buisnesses.objects.all()
    serializer_class = BuisnessesSerializerCustomers
    
    def get(self , request):
        bid = request.GET.get('bid')
                        
                        
        
        buisness = Buisnesses.objects.get(id=bid)
        BuisnessScore(buisness)
        print()
        
        
        

        if bid:
            try:
                buisness = Buisnesses.objects.get(id=bid)
                buisness.no_of_views += 1
                buisness.save()
                tracker=BuisnessTracker.objects.create(buisness=buisness)
                tracker.save()

                if buisness.buisness_type == 'service':
                    services = Services.objects.filter(buisness=buisness)
                    
                    return Response(    
                                        {   
                                            'buisness':self.serializer_class(buisness).data,
                                            'services':ServiceSerializer(services , many=True).data,
                                            'products':[],
                                            'tracker_id':tracker.id
                                        },
                                        status=status.HTTP_200_OK
                                    )
                elif buisness.buisness_type == 'product':
                    products = Products.objects.filter(buisness=buisness)
                    
                    
                    return Response(    
                                        {   
                                            'buisness':self.serializer_class(buisness).data,
                                            'products':ProductSerializer(products , many=True).data,
                                            'services':[],
                                            'tracker_id':tracker.id
                                        },
                                        status=status.HTTP_200_OK
                                    )
            except:
                return Response('No Buisnesess Found',status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('')



class BuisnessImages(generics.ListCreateAPIView):
    queryset = Buisness_pics.objects.all()
    serializer_class = BuisnessPicsSerializer
    
    def get(self , request):
        bid = request.GET.get('bid')
        images=Buisness_pics.objects.filter(buisness=Buisnesses.objects.get(id=bid))
        
        return Response(BuisnessPicsSerializer(images,many=True).data,status=status.HTTP_200_OK)






from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags


def send_otp_email(firstname,otp,toemail):
    subject = 'Your OTP for Email Verification'
    html_message = render_to_string('email_otp.html', {
    'name': firstname,
    'otp': otp
    })
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
    subject,
    plain_message,
    'brandsinfoguide@gmail.com',  # Replace with your "from" email address
    [toemail]    
    )
    email.attach_alternative(html_message, 'text/html')
    email.send()


@api_view(['POST'])    
def addemail(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        email=data.get('email')
        bid=data.get('bid')
        otp=generate_random_otp()
        cache.set(
            f'otp_{email}',
            value={'otp': otp, 'phone': email , 'bid':bid},
            timeout=600 
        )
        cache_data=cache.get(f'otp_{email}')
        print(cache_data)
        send_otp_email(request.user,otp,email)

        return Response('')
    return Response('Authentication Required')
    
    

@api_view(['POST'])
def resendemailotp(request):
    data = json.loads(request.body)
    email = data.get('email')
    cache_data=cache.get(f'otp_{email}')
    if cache_data is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        otp=generate_random_otp()
        cache_data['otp']=otp
        cache.set(f'otp_{email}',value=cache_data, timeout=600)
        send_otp_email(request.user,otp,email)
        return Response(status=status.HTTP_200_OK)
    
    
    
    
@api_view(['POST'])
def verifyemailotp(request):
    data    = json.loads(request.body)
    email   = data.get('email')
    otp     = data.get('otp')
    cache_data=cache.get(f'otp_{email}')
    print(cache_data)
    if cache_data is None:
        return Response('otp expired',status=status.HTTP_400_BAD_REQUEST)
    else:
        print(cache_data['otp'])
        print(otp)
        if otp == cache_data['otp'] :
            buisness=Buisnesses.objects.get(id=cache_data['bid'])
            buisness.email=email
            buisness.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
            
    
    
    
    

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




class AddProductWithImagesView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    queryset = Products.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request):
        bid=request.GET.get('bid')
        if not bid :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = Products.objects.filter(buisness=Buisnesses.objects.get(id=bid))
        print(queryset[0])
        return Response(ProductSerializer(queryset , many=True).data , status=status.HTTP_200_OK)
        
    def create(self, request, *args, **kwargs): 
        print('fffffffffffffffffffffffffffffffffffffffffffff')       
        data = request.data
        print(data)
        images = request.FILES.getlist('images[]')  
        data.setlist('images', images)  
        serializer = ProductCreateSerializer(data=data)
        print(data)
        
        if serializer.is_valid():
            print(" ")
            product = serializer.save()
            return Response({'buisness_type':Buisnesses.objects.get(id=data.get('buisness')).buisness_type}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    

class ProductDelete(generics.DestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access




class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Services.objects.all()
    serializer_class = CreateServiceSerializer
    parser_classes = [MultiPartParser, FormParser]  # Allows image uploads
    filter_backends = [filters.SearchFilter]  
    search_fields = ['buisness']  # Enables filtering by business ID

    def get(self, request):
        bid=request.GET.get('bid')
        if not bid :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = Services.objects.filter(buisness=Buisnesses.objects.get(id=bid))
        print(queryset[0])
        return Response(ServiceSerializer(queryset , many=True).data)
        
    def post(self, request, *args, **kwargs):
        print(request.data)
        return super().post(request, *args, **kwargs)

    
    
    
    
class ServiceCats(generics.ListCreateAPIView):
    queryset = Service_Cats.objects.all()
    serializer_class = ServiceCatsSerializer
        
    
    


class ServiceDelete(generics.DestroyAPIView):
    queryset = Services.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    
    
    
    
# def create_descriptive_cats(bid):
    
#     buisness=Buisnesses.objects.get(id=bid)
#     products = Products.objects.filter(buisness=buisness)
    
#     print(buisness.buisness_type)
#     print(products[0].name)

#     for i in products:
#         print(i.name) 
#         if buisness.buisness_type == 'product'   :
#             print(i.name+' '+'Dealer')
        

    

class Popular_general_cats_view(generics.ListAPIView):
    queryset = Popular_General_Cats.objects.all()   
    serializer_class = Popular_general_cats_serializer
    
    
    
    

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
    result={}
    for title  in Home_Titles.objects.all():
        result[title]=''
    return Response('ihb')



# @api_view(['GET'])
# def HomeView(request):
#     result=[]
#     r={}
#     gencats = Home_Popular_General_Cats.objects.all()
#     r[gencats[0].title.title]=gencats
#     result.append(r)
    
    
#     subcats = Home_Popular_Des_Cats.objects.all()
#     r[subcats[0].title.title]=subcats
#     result.append(r)
    
    
#     pcats   = Home_Popular_Product_Cats.objects.all()
#     r[pcats[0].title.title]=pcats
#     result.append(r)
    
    
#     cities  = Home_Popular_Cities.objects.all()
#     r[cities[0].title.title]=cities
#     result.append(r)
    
    
#     titles  = Home_Titles.objects.all()
#     r[titles[0].title.title]=titles
#     result.append(r)
    
#     print(result)
    
#     return Response('result')
    
    


@api_view(['GET'])
def elasticsearch(request):
    result=Buisnesses.objects.all()
    
    return Response(BuisnessesSerializer(result , many=True).data)

# @api_view(['GET'])
# def elasticsearch(request):
#     query = request.GET.get('q','')
#     print(query)
#     # Perform a multi-table search
#     # search_query = Q("multi_match", query=query, fields=["name"],fuzziness="AUTO", max_expansions=50 ,    prefix_length=2  )
#     # search_query = Q("match", name={"query": query, "fuzziness": "AUTO" , })
#     search_query = Q("prefix", name=query.lower())
    
#     products            = ProductDocument.search().query(search_query).to_queryset()
#     services            = ServiceDocument.search().query(search_query).to_queryset()
#     buisnesses_direct   = BuisnessDocument.search().query(search_query).to_queryset()
#     bdcats              = BDesCatDocument.search().query(search_query).to_queryset()
#     pscats              = PSubCatsDocument.search().query(search_query).to_queryset()
    
#     product_buisness_ids = products.values_list('buisness', flat=True).distinct()
#     service_buisness_ids = services.values_list('buisness', flat=True).distinct()
#     bdcats_buisness_ids  = bdcats.values_list('buisness', flat=True).distinct()
#     # pscats_buisness_ids  = pscats.values_list('buisness', flat=True).distinct()
    
#     print('bdcats:' , bdcats_buisness_ids)
#     print('')
#     # print('pscats', pscats_buisness_ids)
#     print('')
#     print("Buisnesses:",buisnesses_direct)


#     buisnesses = Buisnesses.objects.filter(id__in=set(product_buisness_ids) | set(service_buisness_ids))
#     print(buisnesses)
    
#     if buisnesses_direct :
#         return Response(BuisnessesSerializer(buisnesses_direct , many=True).data)
#     # elif bdcats :
#         # buisnesses = Buisnesses.objects.filter(id__in=set(product_buisness_ids) | set(service_buisness_ids))

    
   
#     # results = list(products)
#     # results2 = list(services)
#     # print(results)
#     # print(results2)

#     s = Search(index="search_index").extra(size=10000)  # Ensure you're fetching all data
#     print("Total documents in index:", s.count())  

#     print(s)  

  
#     return Response(BuisnessesSerializer(buisnesses , many=True).data)
#     # return Response({"product":ProductSerializer(products).data , "services":ServiceSerializer(services).data})
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def HomeView(request):
    result = {}

    # Get all objects
    gencats = Home_Popular_General_Cats.objects.all()
    subcats = Home_Popular_Des_Cats.objects.all()
    pcats = Home_Popular_Product_Cats.objects.all()
    cities = Home_Popular_Cities.objects.all()
    titles = Home_Titles.objects.all()

    # Serialize data
    if gencats.exists():
        result[gencats[0].title.title] = HomePopularGeneralCatsSerializer(gencats, many=True).data

    if subcats.exists():
        result[subcats[0].title.title] = HomePopularDesCatsSerializer(subcats, many=True).data

    if pcats.exists():
        result[pcats[0].title.title] = HomePopularProductCatsSerializer(pcats, many=True).data

    if cities.exists():
        result[cities[0].title.title] = HomePopularCitiesSerializer(cities, many=True).data

    if titles.exists():
        result["home_titles"] = HomeTitlesSerializer(titles, many=True).data

    return Response(result)
