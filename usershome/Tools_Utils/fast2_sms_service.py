import requests
import random
from brandsinfo.settings import FAST2SMS_API_KEY as API_KEY


SENDER_ID = 'SENDER_ID'  
API_URL = "https://www.fast2sms.com/dev/bulkV2"

# overallurl ='https://www.fast2sms.com/dev/bulkV2?authorization=TNuYH9rIb5d7cM6UhWglVmB2vQEieXFKD314RJsStPCLGk08fAOnKw9RlTU30emkyMSD8uXqtfbJgcvW&route=otp&variables_values=123456&flash=0&numbers=7034761676&schedule_time='

def send_otp(mobile_number,otp):
    
   
        
    url = "https://www.fast2sms.com/dev/bulkV2"

    querystring = {"authorization":API_KEY,"message":"This is test message","language":"english","route":"q","numbers":"7034761676"}

    headers = {
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)
    if response.status_code == 200:
        return print("OTP sent successfully")
    else:
        raise Exception("Error sending OTP")
    
    
    
    
    
    
    












