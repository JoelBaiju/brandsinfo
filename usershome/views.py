import json
import secrets
import string
from urllib.parse import urljoin, urlparse
from itertools import chain
import traceback

# Django imports
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

from django.db import IntegrityError

# DRF imports
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser 
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView



# Local app imports
from .sitemap_view import Site_Map_Generator_SB
from .models import *
from .serializers import * 
from .searcher import find_closest 
from brandsinfo.settings import BACKEND_BASE_URL_FOR_SM_SECURE
from . import auth_views
from .utils import *








class BuisnessesView(generics.ListAPIView):
    queryset = Buisnesses.objects.all()
    serializer_class = BuisnessesSerializer

    def get_queryset(self):
        # Optionally, filter the queryset if you want to return buisnesses associated with the user
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
                try:
                    
                    buisness = Buisnesses.objects.get(id=bid)
                    buisness.score=BuisnessScore(buisness)
                    buisness.save()
                    user = Extended_User.objects.get(username=self.request.user)
                    offers = Buisness_Offers.objects.filter(buisness=buisness)
                    offers = BuisnessOffersSerializer(offers , many=True)
                    
                    formatt = request.GET.get('formatt')
                    print(formatt)
                    visitanalysis=buisness_visits_analyzer(buisness =buisness , formatt=formatt)
     

                    if buisness.buisness_type == 'service':
                        services = Services.objects.filter(buisness=buisness)
                        
                        return Response(    
                                            {   
                                                'buisness':BuisnessesSerializerFull(buisness).data,
                                                'offers':offers.data,
                                                'services':ServiceSerializer(services , many=True).data,
                                                'analytics':{
                                                                'average_time_spend':'0',
                                                                'keywords':['hospital','workshop','restaurant']      ,
                                                                'leads':'56',
                                                                'profile_views_progress':'43',                 
                                                                'most_serched_services':Most_searched_services_in_buisness(buisness),
                                                                'most_serched_products':[],
                                                                'searched':buisness.searched,
                                                                'visits':visitanalysis       
                                                            },
                                                'products':[],
                                                'user': UserSerializer(user).data
                                            },
                                            status=status.HTTP_200_OK
                                        )
                    elif buisness.buisness_type == 'product':
                        print('jeei')
                        products = Products.objects.filter(buisness=buisness)
                        
                        
                        return Response(    
                                            {   
                                                'buisness':BuisnessesSerializerFull(buisness).data,
                                                'offers':offers.data,
                                                'products':ProductSerializer(products , many=True).data,
                                                'analytics':{
                                                                'average_time_spend':'0',
                                                                'keywords':['hotel','bank','store'],
                                                                'leads':'56',
                                                                'profile_views_progress':'43',
                                                                'most_serched_products':Most_searched_products_in_buisness(buisness),
                                                                'most_serched_services':[],
                                                                'searched':buisness.searched,
                                                                'visits':visitanalysis

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
                        print('sfsoasaoosjfsofjsfjsf samosa')
                        return Response(    
                                            {   
                                                'buisness':BuisnessesSerializerFull(buisness).data,
                                                'offers':offers.data,
                                                'services':ServiceSerializer(services , many=True).data,
                                                'analytics':{
                                                                'average_time_spend':'0',
                                                                'keywords':['hospital','workshop','restaurant'],
                                                                'leads':'56',
                                                                'profile_views_progress':'43',
                                                                'most_serched_products':Most_searched_products_in_buisness(buisness),
                                                                'most_serched_services':Most_searched_services_in_buisness(buisness),
                                                                'searched':buisness.searched,
                                                                'visits':visitanalysis       
  
                                                                                                                        
                                                            },
                                                'products':ProductSerializer(products , many=True).data,
                                                'user': UserSerializer(user).data
                                            },
                                            status=status.HTTP_200_OK
                                        )

                        
                except Exception as e:
                    print(f"Error: {str(e)}") 
                    return Response(f'No Buisnesess Found{e}',status=status.HTTP_400_BAD_REQUEST)

            else:
                qset = self.get_queryset()
                try:
                    buisnesses = BuisnessesSerializerMini(qset[0] , many=True).data
                except Exception as e:
                    print(e)
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
        print('incoming dataa hereeeee',request.data)
        if serializer.is_valid():
            # print(serializer.data)

            business = serializer.save(owner = request.user)
            print(business.city)
            return Response(
                self.serializer_class(business).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
   
    
    
    
    
def tracker_addtime(self , request):
    
    return Response(status=status.HTTP_200_OK)



  # For detailed error logs


class BuisnessesEdit(generics.UpdateAPIView):
    queryset = Buisnesses.objects.all()
    serializer_class = BuisnessesSerializer
    permission_classes = [IsAuthenticated]

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
    

class BuisnessesShortView(generics.ListAPIView):
    queryset = Buisnesses.objects.all()
    serializer_class = BuisnessesSerializerShort
    
    def get(self , request):    
        bid = request.GET.get('bid')
        if not bid:
            return Response({'error': 'Business ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        buisness = Buisnesses.objects.get(id=bid)
        return Response(self.serializer_class(buisness).data, status=status.HTTP_200_OK)    


class BuisnessesView_for_customers(generics.ListAPIView):
    queryset = Buisnesses.objects.all()
    serializer_class = BuisnessesSerializerCustomers
    
    def get(self , request):
        maping_id = request.GET.get('maping_id')
        print(maping_id)
        sitemap_obj = Sitemap_Links.objects.get(id=maping_id)
        buisness = sitemap_obj.buisness
        print()
        reviewed=None
        visit_tracker = BuisnessVisitTracker.objects.create(buisness=buisness)
        if request.user.is_anonymous == False:
            user=Extended_User.objects.get(username=request.user)
            reviewed = Reviews_Ratings.objects.filter(user=user,buisness=buisness).exists()
            visit_tracker.user=user
            print("checked reviewed : " , reviewed)
        visit_tracker.save()
        
        if buisness:
            BuisnessScore(buisness)
            try:
                buisness.no_of_views += 1
                buisness.save()
                tracker=BuisnessTracker.objects.create(buisness=buisness)
                tracker.save()
                offers = Buisness_Offers.objects.filter(buisness=buisness)
                offers = BuisnessOffersSerializer(offers , many=True)
                if buisness.buisness_type == 'service':
                    services = Services.objects.filter(buisness=buisness)
        
                    return Response(    
                                        {   
                                            'buisness':self.serializer_class(buisness).data,
                                            'offers':offers.data,
                                            'services':ServiceSerializer(services , many=True).data,
                                            'products':[],
                                            'tracker_id':tracker.id,
                                            'reviewed':reviewed,
                                            'dcats':BuisnessDcats(buisness),
                                            'analytics':{
                                                            'average_time_spend':'0',
                                                            'keywords':['hospital','workshop','restaurant'] ,
                                                            'most_serched_products':Most_searched_products_in_buisness(buisness),
                                                            'most_serched_services':Most_searched_services_in_buisness(buisness),
                                                            'searched':buisness.searched,
                                                            'no_of_enquiries':number_of_enquiries(buisness),
                                                            
                                                        }
                                        },
                                        status=status.HTTP_200_OK
                                    )
                elif buisness.buisness_type == 'product':
                    products = Products.objects.filter(buisness=buisness)
                    
                    
                    return Response(    
                                        {   
                                            'buisness':self.serializer_class(buisness).data,
                                            'offers':offers.data,
                                            'products':ProductSerializer(products , many=True).data,
                                            'services':[],
                                            'tracker_id':tracker.id,
                                            'reviewed':reviewed,
                                            'dcats':BuisnessDcats(buisness),
                                            'most_serched_products':Most_searched_products_in_buisness(buisness),
                                            'most_serched_services':Most_searched_services_in_buisness(buisness),
                                            'searched':buisness.searched,
                                            'no_of_enquiries':number_of_enquiries(buisness),

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
                                                'buisness':self.serializer_class(buisness).data,
                                                'offers':offers.data,
                                                'services':ServiceSerializer(services , many=True).data,
                                                'dcats':BuisnessDcats(buisness),
                                                'analytics':{
                                                                'average_time_spend':'0',
                                                                'keywords':['hospital','workshop','restaurant'] ,
                                                                'most_serched_products':Most_searched_products_in_buisness(buisness),
                                                                'most_serched_services':Most_searched_services_in_buisness(buisness),
                                                                'searched':buisness.searched,
                                                                'no_of_enquiries':number_of_enquiries(buisness),
                                                                                                                          
                                                            },
                                                'products':ProductSerializer(products , many=True).data,
                                                'reviewed':reviewed

                                            },
                                            status=status.HTTP_200_OK
                                        )
            except Exception as e:
                print(e)
                return Response('No Buisnesess Found',status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('')
        
    

def Get_location_view(request,bid):
    if request is None:
        return render(request,'addlocation.html',{'bid':bid})
    lon = request.GET.get('lon')
    lat = request.GET.get('lat')
    bid = request.GET.get('bid')
    
    print(lon,lat,bid)
    
    if lon and lat and bid:
        buisness = Buisnesses.objects.get(id=int(float(bid)))
        buisness.latittude = lat
        buisness.longitude = lon
        buisness.save()
        return render(request,'ThankYou.html',{'bid':bid})
    
    


class BuisnessImages(generics.ListCreateAPIView):
    queryset = Buisness_pics.objects.all()
    serializer_class = BuisnessPicsSerializer
    
    def get(self , request):
        bid = request.GET.get('bid')
        images=Buisness_pics.objects.filter(buisness=Buisnesses.objects.get(id=bid))
        
        return Response(BuisnessPicsSerializer(images,many=True).data,status=status.HTTP_200_OK)
    
    
    def post(self, request):
        print(request.data)
        bid = request.data.get('buisness')  # Expecting 'buisness' field in request
        if not bid:
            print('id error')
            return Response({'error': 'Business ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            buisness = Buisnesses.objects.get(id=bid)
        except Buisnesses.DoesNotExist:
            print('buisness error')
            return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)

        images = request.FILES.getlist('images[]')  # Get multiple images from request

        if not images:
            print('image error')
            return Response({'error': 'No images uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        created_images = []
        for img in images:
            buisness_pic = Buisness_pics.objects.create(buisness=buisness, image=img)
            created_images.append(buisness_pic)

        return Response(BuisnessPicsSerializer(created_images, many=True).data, status=status.HTTP_201_CREATED)







class BuisnessPics_Delete(generics.DestroyAPIView):
    queryset = Buisness_pics.objects.all()
    serializer_class = BuisnessPicsSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            error_message = str(e)
            traceback.print_exc()  # Prints the full traceback in the console

            return Response(
                {"error": error_message},   
                status=status.HTTP_400_BAD_REQUEST
            )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_bookmarked(request):
    bid = request.GET.get('bid')

    if not bid:
        return Response({'error': 'Business ID (bid) is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        business = get_object_or_404(Buisnesses, id=bid)

        is_bookmarked = Liked_Buisnesses.objects.filter(buisness=business, user=request.user).exists()

        return Response({'Bookmarked': is_bookmarked}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddOfferView(generics.CreateAPIView):
    serializer_class = BuisnessOffersSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Offer added successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GetOffersView(generics.ListAPIView):
    serializer_class = BuisnessOffersSerializer
    queryset = Buisness_Offers.objects.all()
    
    def get(self, request):
        bid = request.GET.get('bid')
        if not bid:
            return Response({'error': 'Business ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            buisness = Buisnesses.objects.get(id=bid)
        except Buisnesses.DoesNotExist:
            return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)

        offers = Buisness_Offers.objects.filter(buisness=buisness)
        return Response(BuisnessOffersSerializer(offers, many=True).data, status=status.HTTP_200_OK)
    
    

class DeleteOfferView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Buisness_Offers.objects.all()
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        offer = self.get_object()
        if offer.buisness.user != request.user:
            return Response({'error': 'Unauthorized to delete this offer'}, status=status.HTTP_403_FORBIDDEN)
        
        self.perform_destroy(offer)
        return Response({'message': 'Offer deleted successfully'}, status=status.HTTP_200_OK)









# Create a group
class Create_Group_View(generics.CreateAPIView):
    serializer_class = LikedBuisnessGroupSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



# Add a business to a group

class Add_Liked_Buisnesses_to_group(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        business_id = request.data.get('bid')

        if not business_id:
            return Response({'error': 'Business ID (bid) is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the business object
            business = get_object_or_404(Buisnesses, id=business_id)
            city_name = business.city.city_name  

            # Get or create a liked business group based on city name
            group, created = Liked_Buisnesses_Group.objects.get_or_create(
                user=request.user,
                name=city_name 
            )

            # Check if the business is already in the group
            liked_obj = Liked_Buisnesses.objects.filter(buisness=business, group=group, user=request.user)
            if liked_obj.exists():
                liked_obj.delete()
                return Response({
                    'message': 'Business removed from group',
                    'group_created': created
                }, status=status.HTTP_200_OK)

            # Create a new liked business entry
            Liked_Buisnesses.objects.create(buisness=business, group=group, user=request.user)
            
            return Response({
                'message': 'Business added to group',
                'group_created': created
            }, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({'error': 'Database integrity error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    
    
# Get all groups for a user
class User_Groups_View(generics.ListAPIView):
    serializer_class = GroupWithbuisnessesSerializer
    permission_classes = [IsAuthenticated]

    # user=Extended_User.objects.get(id=34)
    
    def get_queryset(self):
        # return Liked_Buisnesses_Group.objects.filter(user=self.user)
        return Liked_Buisnesses_Group.objects.filter(user=self.request.user)





# Get buisnesses inside a group
class Group_Buisnesses_View(generics.ListAPIView):
    serializer_class = LikedBusinessSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.request.GET.get('gid')
        if group_id:
            group = Liked_Buisnesses_Group.objects.get(id=group_id)
            return Liked_Buisnesses.objects.filter(group=group)
        return Liked_Buisnesses.objects.none()

    def get(self, request, *args, **kwargs):
        queryset=self.get_queryset()
        buisness=[]
        for i in queryset:
            buisness.append(i.buisness)
        buisness=BuisnessesSerializerShort(buisness ,many=True)
            # print(buisness)
        
        return Response(buisness.data)









class Enquiries_View(generics.ListCreateAPIView):
    serializer_class = EnquiriesSerializer

    def post(self, request):
        data = json.loads(request.body)
        bid = data.get('bid')
        message = data.get('message')
        mobile_number = data.get('mobile_number')
        name = data.get('name')

        if not bid:
            return Response({'error': 'Business ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            buisness = Buisnesses.objects.get(id=bid)
        except Buisnesses.DoesNotExist:
            return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_anonymous:
            print('anonymous')
            print(request.user)
            enquiry_obj=Enquiries.objects.create(buisness=buisness, message=message , mobile_number=mobile_number , name=name)
            return auth_views.signup_request_from_enquiry(name=name , phone=mobile_number , enquiry_id=enquiry_obj.id ) 
        else:
            Enquiries.objects.create(buisness=buisness, message=message , mobile_number=mobile_number , name=name , user=request.user)
            
        return Response({'message': 'Enquiry sent successfully'}, status=status.HTTP_201_CREATED)

    def get(self, request):
        if request.user.is_anonymous:
            return Response('Authentication Required',status=status.HTTP_401_UNAUTHORIZED)
        bid = request.GET.get('bid')
        if  bid:

            try:
                buisness = Buisnesses.objects.get(id=bid)
            except Buisnesses.DoesNotExist:
                return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)
    
            enquiries = Enquiries.objects.filter(buisness=buisness)
        
        else :
            enquiries = Enquiries.objects.filter(user=Extended_User.objects.get(username=request.user))
        
        return Response(EnquiriesSerializer(enquiries, many=True).data, status=status.HTTP_200_OK)



def get_average_rating(business_id):
    # Fetch the average rating for the given business
    average_rating = Reviews_Ratings.objects.filter(
        buisness_id=business_id
    ).aggregate(
        avg_rating=Avg('rating')
    )['avg_rating']

    # If no reviews exist, return 0 or None
    return average_rating if average_rating is not None else 0


class Reviews_Ratings_View(generics.ListCreateAPIView):
    queryset = Reviews_Ratings.objects.all()
    serializer_class = ReviewRatingSerializer
    permission_classes = [IsAuthenticated] 
    
    def post(self, request):
        data = request.data
        bid = data.get('bid')
        rating = data.get('rating')
        review = data.get('review')

        if not bid:
            return Response({'error': 'Business ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            buisness = Buisnesses.objects.get(id=bid)
        except Buisnesses.DoesNotExist:
            return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            User = Extended_User.objects.get(username=request.user)
        except: 
            return Response('User not found')
        
        
        print(request.data)
        
        review_obj = Reviews_Ratings.objects.create(buisness=buisness, rating=rating, review=review , user=User)
        
        images = request.FILES.getlist('images[]')  
        for image in images:
            review_pic = Review_pics.objects.create(review=review_obj, image=image)
            review_pic.save()
            
        review_obj.save()
        
        buisness.total_no_of_ratings = buisness.total_no_of_ratings + 1
        buisness.rating        = get_average_rating(buisness.id)
        buisness.save()
        
        
        
        return Response(ReviewRatingSerializer(review_obj).data, status=status.HTTP_201_CREATED)
    
    
class GetReviewRatingPaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
    
    def _get_custom_url(self, url):
        if not url:
            return None
        # Parse the absolute URL returned by super()
        parsed_url = urlparse(url)
        # Extract the path and query parameters
        path_and_query = parsed_url.path
        if parsed_url.query:
            path_and_query += "?" + parsed_url.query
        # Join with the custom base URL
        return urljoin(BACKEND_BASE_URL_FOR_SM_SECURE, path_and_query)

    def get_next_link(self):
        url = super().get_next_link()
        return self._get_custom_url(url)

    def get_previous_link(self):
        url = super().get_previous_link()
        return self._get_custom_url(url)
    
    
    
def floorit(x):
    floored=int(x)
    if x>floored:
        return floored+1
    else:
        return floored
    
class Get_Reviews_Ratings_View(generics.ListAPIView):
    queryset = Reviews_Ratings.objects.all()
    serializer_class = ReviewRatingSerializer
    pagination_class = GetReviewRatingPaginator
    
    
    def get(self, request):
        bid = request.GET.get('bid')
        if not bid:
            return Response({'error': 'Business ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        else:
           
            try:
                buisness = Buisnesses.objects.get(id=bid)
            except Buisnesses.DoesNotExist:
                return Response({'error': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)
            queryset = Reviews_Ratings.objects.filter(buisness=buisness)
            
            query_count=len(queryset)
            page_count = query_count/10
            page_count=floorit(page_count)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            column_names = self.serializer_class.Meta.fields
            response_data = {
                "column_names": column_names,
                'total_pages':page_count,
                "data": serializer.data,
            }
            return self.get_paginated_response(response_data)  # Return paginated response

            
        


        



















@api_view(['POST'])    
def addemail(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        email=data.get('email')
        bid=data.get('bid')
        otp=auth_views.generate_random_otp()
        cache.set(
            f'otp_{email}',
            value={'otp': otp, 'phone': email , 'bid':bid},
            timeout=600 
        )
        
        try:
            eotp=Email_OTPs.objects.get(email=email)
        except:
            eotp=Email_OTPs.objects.create(email=email,otp=otp)
        eotp.bid=bid
        eotp.otp=otp
        eotp.save()
        
        cache_data=cache.get(f'otp_{email}')
        print(cache_data)
        send_otp_email(request.user,otp,email)

        return Response('')
    return Response('Authentication Required')
    
    

@api_view(['POST'])
def resendemailotp(request):
    data = json.loads(request.body)
    email = data.get('email')
    otp=auth_views.generate_random_otp()
    try: 
        eotp=Email_OTPs.objects.get(email=email)   
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    eotp.otp=otp    
    send_otp_email(request.user,otp,email)
    return Response(status=status.HTTP_200_OK)
    
    
    
    
@api_view(['POST'])
def verifyemailotp(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
        print(otp)

        if not email or not otp:
            return Response({'message': 'email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        eotp = Email_OTPs.objects.get(email=email)
        
        if eotp is None:
            return Response({'message': 'Unknown Error , probably you are invalid'}, status=status.HTTP_400_BAD_REQUEST)

        # print(type(otp))
        # print(type(auth.otp))
        if str(otp) != str(eotp.otp):
            return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        
        user = Extended_User.objects.get(username=request.user)
        user.email=email
        user.save()


    except json.JSONDecodeError:
        return Response({'message': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('message', str(e))
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    return Response('',status=status.HTTP_200_OK)
    
    
    

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
        print('fffffffff')       
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
        images = request.FILES.getlist('images[]')
        data = request.data
        data.setlist('images', images)
        serializer = self.get_serializer(data=data) 
        return super().post(request, *args, **kwargs)

    
    
    
    
class ServiceCats(generics.ListCreateAPIView):
    queryset = Service_Cats.objects.all()
    serializer_class = ServiceCatsSerializer
        
    
    



class ServiceDelete(generics.DestroyAPIView):
    queryset = Services.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    
    
 

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
    print('hereerererersso only ')
    
    if not dcid or not bid:
        return Response('',status=status.HTTP_400_BAD_REQUEST)
    buisness=Buisnesses.objects.get(id=bid)
    for i in dcid:
        print(Descriptive_cats.objects.get(id=i))
        
        Buisness_Descriptive_cats.objects.create(dcat=Descriptive_cats.objects.get(id=i) , buisness=buisness).save()
    
    Site_Map_Generator_SB(buisness=buisness)

    
    return Response('',status=status.HTTP_200_OK)

    
    








    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

@api_view(['GET'])
def HomeView(request):
    result = []

    # Get all objects
    gencats = Home_Popular_General_Cats.objects.all()
    subcats = Home_Popular_Des_Cats.objects.all()
    pcats = Home_Popular_Product_Cats.objects.all()
    cities = Home_Popular_Cities.objects.all()
    meta_data = Home_Meta_data.objects.all()
    ads = Home_Ads.objects.all()

    # Serialize data
    if gencats.exists():
        section={}
        section['title']=gencats[0].title.title
        section['data']=HomePopularGeneralCatsSerializer(gencats, many=True).data
        result.append(section)
        
    if subcats.exists():
        section={}
        section['title']=subcats[0].title.title
        section['data']=HomePopularDesCatsSerializer(subcats, many=True).data
        result.append(section)  

    if pcats.exists():
        section={}
        section['title']=pcats[0].title.title
        section['data']=HomePopularProductCatsSerializer(pcats, many=True).data
        result.append(section)
        
    if cities.exists():
        section={}
        section['title']=cities[0].title.title
        section['data']=HomePopularCitiesSerializer(cities, many=True).data
        result.append(section)
       
    if ads.exists():
        section={}
        section['title']='ADS'
        section['data']=HomeAdsSerializer(ads, many=True).data
        result.append(section)
    
    

   

    return Response({'sections' : result , 'meta_data':HomeMetaDataSerializer(meta_data, many=True).data[0] })









