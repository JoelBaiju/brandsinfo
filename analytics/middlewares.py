import json
from .models import RequestLog

class RequestTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Capture information
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        referer = request.META.get('HTTP_REFERER', '')
        origin = request.META.get('HTTP_ORIGIN', '')
        method = request.method
        path = request.path
        query_params = json.dumps(request.GET.dict())

        # Save to DB
        RequestLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            accept_language=accept_language,
            referer=referer,
            origin=origin,
            method=method,
            path=path,
            query_params=query_params,
        )

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Try to get real IP if behind proxy/load balancer"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

