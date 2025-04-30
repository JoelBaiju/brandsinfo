from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count
from .models import RequestLog
from .serializers import IPLogSerializer  # Import the serializer
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes


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


from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
import logging
from django.utils.timezone import now

logger = logging.getLogger(__name__)

class CustomIPLogPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
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

class IPLogView(APIView):
    """
    API endpoint that returns IP access logs with pagination
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - start_date: Filter logs from this date (YYYY-MM-DD)
    - end_date: Filter logs until this date (YYYY-MM-DD)
    """
    pagination_class = CustomIPLogPagination
    
    def get(self, request):
        try:
            # Get filter parameters
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            # Build query
            query = """
                SELECT 
                    ip_address,
                    GROUP_CONCAT(DISTINCT path) as visited_paths,
                    COUNT(*) as visit_count
                FROM analytics_requestlog
                {where_clause}
                GROUP BY ip_address
                ORDER BY ip_address
            """
            
            where_clause = ""
            params = []
            if start_date and end_date:
                where_clause = "WHERE timestamp BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            elif start_date:
                where_clause = "WHERE timestamp >= %s"
                params.append(start_date)
            elif end_date:
                where_clause = "WHERE timestamp <= %s"
                params.append(end_date)
            
            # Execute query
            with connection.cursor() as cursor:
                cursor.execute(query.format(where_clause=where_clause), params)
                columns = [col[0] for col in cursor.description]
                results = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
            
            # Process results
            for item in results:
                item['visited_paths'] = item['visited_paths'].split(',') if item.get('visited_paths') else []
            
            # Paginate
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(results, request)
            serializer = IPLogSerializer(page, many=True, context={'request': request})
            
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error in IPLogView: {str(e)}", exc_info=True)
            return Response({"error": "An error occurred while processing your request"}, status=500)
        
        
        
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from rest_framework.response import Response
from django.utils.timezone import now
from .models import RequestLog



class LogCountView(APIView):
    def get(self,request):
        
        if request.method == 'GET':
            format = request.GET.get('order_by')

            rl= RequestLog.objects.all()
            for i in rl:
                print(i.timestamp)

            if format == 'week':
                logs = RequestLog.objects.annotate(period=TruncWeek('timestamp')).values('period').annotate(count=Count('id'))
            elif format == 'month':
                logs = RequestLog.objects.annotate(period=TruncMonth('timestamp')).values('period').annotate(count=Count('id'))
            elif format == 'year':
                logs = RequestLog.objects.annotate(period=TruncYear('timestamp')).values('period').annotate(count=Count('id'))
            else:
                today = now().date()
                logs = RequestLog.objects.filter(timestamp__date=today).annotate(period=TruncDay('timestamp')).values('period').annotate(count=Count('id'))

            return Response({'count': logs.count()})
