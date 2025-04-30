from django.contrib import admin
from django.urls import path
from . import views
from . import auth_views



urlpatterns = [
    
    path('login/',auth_views.admin_auth_view),
    path('dash/',views.admin_dashboard_view),   
    path('add-general-cats/', views.AddGeneralCatsView.as_view(), name='add-general-cats'),
    path('add-descriptive-cats/', views.AddDescriptiveCatsView.as_view(), name='add-descriptive-cats'),
]