import requests
import urllib.parse
from rest_framework.decorators import api_view
from rest_framework.response import Response



API_KEY = 'rbdRxHQu02qRCGIU'
SENDER_ID = 'BRNSIF'  # Must be 6 characters
BASE_URL = 'https://text.draft4sms.com/vb/apikey.php'

import requests
import urllib.parse

def send_otp_draft4sms(otp, phone_number):
    TEMPLATE_ID = "1107175023088680702"
   
    message =  f""" 
                    Your BrandsInfo OTP is {otp} . 
                    Valid for 10 mins. Do not share this OTP to anyone. 
                    If you didn't request this .Contact : support@brandsinfo.in
                """
    encoded_message = urllib.parse.quote(message)

    url = (
        f"https://text.draft4sms.com/vb/apikey.php?"
        f"apikey={API_KEY}&senderid={SENDER_ID}&number={phone_number}"
        f"&message={encoded_message}&templateid={TEMPLATE_ID}&format=json"
    )

    try:
        response = requests.get(url)
        print( response.json())
    except requests.RequestException as e:
        print( {'status': 'error', 'message': str(e)})






def send_welcome_draft4sms(name , phone_number):
    TEMPLATE_ID="1107175050843766707"
   
    message = f""" 
                    Hi {name}, welcome to BrandsInfo!
                    List your first business now and grow faster. 
                    Get started at https://brandsinfo.in Help: support@brandsinfo.in 
                """
    encoded_message = urllib.parse.quote(message)

    url = (
        f"https://text.draft4sms.com/vb/apikey.php?"
        f"apikey={API_KEY}&senderid={SENDER_ID}&number={phone_number}"
        f"&message={encoded_message}&templateid={TEMPLATE_ID}&format=json"
    )

    try:
        response = requests.get(url)
        print( response.json())
    except requests.RequestException as e:
        print( {'status': 'error', 'message': str(e)})




def send_buisness_registered_draft4sms(name , phone_number):
    TEMPLATE_ID= "1107175050817862087"
    message = f""" 
                    Congrats {name}! Your business is live on BrandsInfo. Boost visibility with a premium package. 
                    Explore now: www.brandsinfo.in/pricing
                """
    encoded_message = urllib.parse.quote(message)

    url = (
        f"https://text.draft4sms.com/vb/apikey.php?"
        f"apikey={API_KEY}&senderid={SENDER_ID}&number={phone_number}"
        f"&message={encoded_message}&templateid={TEMPLATE_ID}&format=json"
    )

    try:
        response = requests.get(url)
        print( response.json())
    except requests.RequestException as e:
        print( {'status': 'error', 'message': str(e)})



def send_plan_purchased_draft4sms(name,plan,expiry , phone_number):
    print("sms plan purchased ")
    print('phone',phone_number)

    TEMPLATE_ID="1107175050829654296"
   
    message = f""" 
                    Hi {name}, your {plan} package is active till {expiry}. 
                    Enjoy better visibility and more leads. Let's grow together -BrandsInfo.
                """
    encoded_message = urllib.parse.quote(message)

    url = (
        f"https://text.draft4sms.com/vb/apikey.php?"
        f"apikey={API_KEY}&senderid={SENDER_ID}&number={phone_number}"
        f"&message={encoded_message}&templateid={TEMPLATE_ID}&format=json"
    )

    try:
        response = requests.get(url)
        print( response.json())
    except requests.RequestException as e:
        print( {'status': 'error', 'message': str(e)})




@api_view(['GET'])
def senddd(request):
    print(send_otp_draft4sms("12345" , "7034761676"))

    return Response('fonsofnsf')






