from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import RequestLog
import json

@csrf_exempt
def track_visit(request):
    if request.method == 'POST':
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        referer = request.META.get('HTTP_REFERER', '')
        origin = request.META.get('HTTP_ORIGIN', '')
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}

        path = data.get('path', '')
        extra = data.get('extra', '')

        # Check if IP already exists
        if RequestLog.objects.filter(ip_address=ip_address, path=path, method='VISIT').exists():
            return JsonResponse({'status': 'already_tracked'})

        # Save if not already tracked
        RequestLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            accept_language=accept_language,
            referer=referer,
            origin=origin,
            method='VISIT',  # Custom method to distinguish
            path=path,
            query_params=extra,
        )

        return JsonResponse({'status': 'ok'})
    
    return JsonResponse({'error': 'invalid method'}, status=400)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
