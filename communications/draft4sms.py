import requests
import urllib.parse
from rest_framework.decorators import api_view
from rest_framework.response import Response



def send_sms_draft4sms():
    phone_numbers = ["7559946420"]
    message = 'helloooo hai testing from berlin '
    """
    Sends SMS using Draft4SMS API.

    Args:
        message (str): Message content to be sent.
        phone_numbers (list or str): Single number or list of numbers.

    Returns:
        dict: API response as dictionary.
    """
    API_KEY = 'rbdRxHQu02qRCGIU'
    SENDER_ID = 'BRNSIF'  # Must be 6 characters
    BASE_URL = 'https://text.draft4sms.com/vb/apikey.php'

    # Ensure numbers are in comma-separated string
    if isinstance(phone_numbers, list):
        number_string = ",".join(phone_numbers)
    else:
        number_string = phone_numbers

    # URL encode the message
    encoded_message = urllib.parse.quote(message)

    # Construct final URL
    url = f"{BASE_URL}?apikey={API_KEY}&senderid={SENDER_ID}&number={number_string}&message={encoded_message}&format=json"
    url = f"https://text.draft4sms.com/vb/apikey.php?apikey=rbdRxHQu02qRCGIU&senderid=BRNSIF&templateid=otptemplate1&number=7034761676&message=Hello There"
    try:
        response = requests.get(url)
        return response.json()
    except requests.RequestException as e:
        return {'status': 'error', 'message': str(e)}





@api_view(['GET'])
def senddd(request):
    print(send_sms_draft4sms())

    return Response('fonsofnsf')






