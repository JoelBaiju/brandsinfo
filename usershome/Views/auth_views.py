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
from ..models import *
from ..serializers import * 
from brandsinfo.settings import FIREBASE_API_KEY






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
        try:
            auth=Auth_OTPs.objects.get(phone=phone)
        except:
            auth=Auth_OTPs.objects.create(phone=phone,otp=otp)
        auth.exists=exists
        auth.otp=otp
        auth.save()
        
       
        # send_otp(phone, otp)
        return Response({'exists': exists,'otp':otp},status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({'success': False, 'message': 'Invalid JSON format.'}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        # Log or print error for debugging purposes
        print(f"Error in signup_request_1: {str(e)}")
        return Response({'success': False, 'message': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






def create_new_user(phone, auth, utype):
    user = Extended_User.objects.create_user(
        username=phone,
        password=phone + auth.name,
        mobile_number=phone,
        first_name=auth.name
    )
    if utype == 'customer':
        user.is_customer = True
    elif utype == 'buisness':
        user.is_vendor = True
    user.save()
    return user

def link_user_to_enquiry(auth, user):
    enquiry_id = auth.enquiry
    if enquiry_id:
        enquiry = get_object_or_404(Enquiries, id=enquiry_id)
        enquiry.user = user
        enquiry.save()






import requests
import json


def verify_token(id_token):
    url = f'https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}'
    
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'idToken': id_token})
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Token verification failed')

# def verifyotp(request, utype, from_enquiry=False):
#     try:
#         data = json.loads(request.body)
#         phone = data.get('phone')
#         otp = data.get('otp')
#         print(otp , phone)
        

#         if not phone or not otp:
#             return Response({'message': 'Phone and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

#         auth = Auth_OTPs.objects.get(phone=phone)
        
#         if auth is None:
#             return Response({'message': 'OTP Expired'}, status=status.HTTP_400_BAD_REQUEST)

#         # print(type(otp))
#         # print(type(auth.otp))
#         if str(otp) != str(auth.otp):
#             return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

#         if auth.exists:
#             user = get_object_or_404(Extended_User, username=auth.phone)
#         else:
#             user = create_new_user(phone, auth, utype)

#         if from_enquiry:
#             link_user_to_enquiry(auth, user)

#         refresh = RefreshToken.for_user(user)
#         return Response({
#             'message': 'OTP Verified',
#             'exists': auth.exists,
#             'sessionid': str(refresh.access_token),
#             'refresh_token': str(refresh)
#         }, status=status.HTTP_201_CREATED)

#     except json.JSONDecodeError:
#         return Response({'message': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         print('message', str(e))
#         return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def verifyotp(request, utype, from_enquiry=False):
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        token = data.get('idToken')

        if not phone :
            print('phone not in request')
            return Response({'message': 'Phone and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
        if not token :
            print('phone not in token')
            return Response({'message': 'Phone and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        auth = Auth_OTPs.objects.get(phone=phone)
        
        if auth is None:
            print('auth object not found')
            return Response({'message': 'invalid error'}, status=status.HTTP_400_BAD_REQUEST)

       
        if verify_token(token)==False:
            print('token verification failed')
            return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        if auth.exists:
            user = get_object_or_404(Extended_User, username=auth.phone)
        else:
            print('auth not found')
            try:
                user = create_new_user(phone, auth, utype)
            except Exception as e :
                print(e)
                print('user creation exeption occured')
        if from_enquiry:
            link_user_to_enquiry(auth, user)

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'OTP Verified',
            'exists': auth.exists,
            'sessionid': str(refresh.access_token),
            'refresh_token': str(refresh)
        }, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        return Response({'message': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('message', str(e))
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def verifyotp_customers(request):
    return verifyotp(request , utype = 'customer')


@api_view(['POST'])
def verifyotp_buisnesses(request):
    return verifyotp(request , utype = 'buisness')


@api_view(['POST'])
def verifyotp_from_enquiry(request):
    return verifyotp(request , utype = 'customer' ,from_enquiry=True)




@api_view(['POST'])    
def signup_request_2(request):
    
    data=json.loads(request.body)
    phone=data.get('phone')
    name=data.get('name')
    try:
        auth = Auth_OTPs.objects.get(phone=phone)
        auth.name = name
        auth.save()
        return Response({
                     'message':'Name Saved',
                    } ,status=status.HTTP_200_OK)  
    except:
        return Response({
                     'message':'Auth credentials wrong',
                    } ,status=status.HTTP_400_BAD_REQUEST)  

  
    
     



@api_view(['POST'])
def resendotp(request):
    data=json.loads(request.body)
    phone=data.get('phone')
    
    otp=generate_random_otp()
    
    
    auth = Auth_OTPs.objects.get(phone=phone)
    auth.otp = otp
    auth.save()
    print(otp)
                                    
    return Response({'message':'Otp sent sucessfully'},status=status.HTTP_200_OK)
    
    
    
    
# =================================================================================================================

















def signup_request_from_enquiry(name,phone,enquiry_id):
   
    try:
        exists = Extended_User.objects.filter(username=phone).exists()
        
        otp = generate_random_otp()
        
        cache.set(
            f'otp_{phone}',
            value={'otp': otp,'name':name,'enquiry_id':enquiry_id, 'phone': phone, 'exists': exists , 'name':'' },
            timeout=600  
        )
        # send_otp(phone, otp)
        try:
            auth=Auth_OTPs.objects.get(phone=phone)
        except:
            auth=Auth_OTPs.objects.create(phone=phone,otp=otp)
        auth.name=name
        auth.enquiry=enquiry_id
        auth.exists=exists
        auth.otp=otp
        auth.save()
        return Response({'exists': exists,'otp':otp},status=status.HTTP_200_OK)


    except Exception as e:

        print(f"Error in signup_request_1: {str(e)}")
        return Response({'success': False, 'message': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








class User_Data(generics.ListAPIView):
    queryset = Extended_User.objects.all()
    serializer_class = UserSerializer

    def get(self , request):
        if request.user.is_authenticated:
            user = Extended_User.objects.get(username=request.user)
            return Response(self.serializer_class(user).data, status=status.HTTP_200_OK)
        return Response('Authentication required' , status=status.HTTP_401_UNAUTHORIZED)







# ==========================================================================

from django.contrib.auth import authenticate,login,logout


def Admin_auth_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    
    user =authenticate(username=username , password = password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'OTP Verified',
            'sessionid': str(refresh.access_token),
            'refresh_token': str(refresh)
        }, status=status.HTTP_201_CREATED)
    else:
        return Response('Gotchaa :)  Now Get lost')