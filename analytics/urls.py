from django.contrib import admin
from django.urls import path
from . import views



urlpatterns = [
    
    path('track_visit/',views.track_visit ),   
    path('get_ip_logs/',views.IPLogView.as_view(), name='get_ip_logs'),  
    path('log_count/',views.LogCountView.as_view(), name='log_count'),
]