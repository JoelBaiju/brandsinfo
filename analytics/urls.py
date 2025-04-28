from django.contrib import admin
from django.urls import path
from . import views



urlpatterns = [
    
    path('track_visit/',views.track_visit ),   
]