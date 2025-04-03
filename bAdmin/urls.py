from django.contrib import admin
from django.urls import path
from . import views
from . import auth_views



urlpatterns = [
    
    path('login/',auth_views.admin_auth_view),
    
]