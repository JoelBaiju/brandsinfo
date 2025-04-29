from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count
from .models import RequestLog
from .serializers import IPLogSerializer  # Import the serializer
import json
from rest_framework.views import APIView
from rest_framework.response import Response

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




from rest_framework.pagination import PageNumberPagination

class CustomIPLogPagination(PageNumberPagination):
    page_size = 20  # Default page size
    page_size_query_param = 'page_size'  # Allow client to override
    max_page_size = 100  # Maximum limit
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page_size': self.get_page_size(self.request),
            'results': data
        })
        
        
        
        
from django.db.models import Count, F, Value
from django.db.models.functions import Concat, GroupConcat

class IPLogView(APIView):
    def get(self, request):
        # MySQL compatible version using GROUP_CONCAT
        queryset = RequestLog.objects.values('ip_address').annotate(
            visited_paths=GroupConcat('path', distinct=True),
            visit_count=Count('id')
        ).order_by('ip_address')
        
        # Create paginator instance
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 20)
        
        # Paginate the queryset
        page = paginator.paginate_queryset(queryset, request)
        
        # Convert the GROUP_CONCAT string to a list
        for item in page:
            item['visited_paths'] = item['visited_paths'].split(',') if item['visited_paths'] else []
        
        serializer = IPLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)