from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.env import Env
import os


client_id='SU2504091720243320731397',
client_secret='20435b66-f622-4903-ba22-40bead21262e',
client_version=1,
env=Env.PRODUCTION

# client = StandardCheckoutClient.get_instance(
#     client_id='TEST-M22HLXACRTTPK_25041',
#     client_secret='MzExODRmMmQtYTEzYi00Yjg2LTkwMDQtODYzZTVhMjg4ZDRm',
#     client_version=1,
#     env=Env.SANDBOX 
# )

client = StandardCheckoutClient.get_instance(
    client_id='SU2504091720243320731397',
    client_secret='20435b66-f622-4903-ba22-40bead21262e',
    client_version=1,
    env=Env.PRODUCTION  # Change to Env.PRODUCTION for live
)
PHONEPE_REDIRECT_URL = "https://brandsinfo.in/pricing/success/"









from uuid import uuid4
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest

def initiate_payment(amount_in_rupees):
    try:
        request = StandardCheckoutPayRequest.build_request(
            merchant_order_id=f"ORDER_{uuid4().hex[:10]}", 
            amount=amount_in_rupees * 100,  
            # amount=100,              
            redirect_url=PHONEPE_REDIRECT_URL,
          
        )
        
        response = client.pay(request)
        if response:
            return {
                'success': True,
                'redirect_url': response.redirect_url,
                'order_id': request.merchant_order_id,
                'response': response,  
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
        
        
        
        
        
        
        
        
def check_payment_status(order_id):
    try:
        response = client.get_order_status(order_id)
        return {
            'status': response.state.value,  # e.g., "COMPLETED", "FAILED"
            'transaction_id': response.transaction_id,
            'amount': response.amount / 100  # Convert paise to rupees
        }
    except Exception as e:
        return {'error': str(e)}
    
    
    
    
def validate_callback(auth_header: str, raw_body: str):
    """Validate server-to-server callback"""
    try:
        # Store these securely in environment variables
        callback_creds = {
            'username': os.getenv('PHONEPE_CALLBACK_USER'),
            'password': os.getenv('PHONEPE_CALLBACK_PASS')
        }
        
        response = client.validate_callback(
            username=callback_creds['username'],
            password=callback_creds['password'],
            callback_header_data=auth_header,
            callback_response_data=raw_body
        )
        
        return {
            'valid': True,
            'order_id': response.order_id,
            'status': response.state.value
        }
    except Exception as e:
        return {'valid': False, 'error': str(e)}