import base64
import hashlib
import hmac
import json
import requests
from django.conf import settings

def create_phonepe_request(payload: dict) -> dict:
    json_payload = json.dumps(payload, separators=(',', ':'))
    base64_payload = base64.b64encode(json_payload.encode()).decode()
    final_string = f"/pg/v1/pay{base64_payload}{settings.PHONEPE_SALT_KEY}"
    x_verify = hmac.new(
        settings.PHONEPE_SALT_KEY.encode(),
        final_string.encode(),
        hashlib.sha256
    ).hexdigest() + "###" + settings.PHONEPE_SALT_INDEX

    return {
        "base64_payload": base64_payload,
        "x_verify": x_verify,
    }
