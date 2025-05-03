from django.contrib import admin
from django.urls import path
from . import views
from . import auth_views



urlpatterns = [
    
    path('login/',auth_views.admin_auth_view),
    path('dash/',views.admin_dashboard_view),   
    path('add-general-cats/', views.AddGeneralCatsView.as_view(), name='add-general-cats'),
    path('add-descriptive-cats/', views.AddDescriptiveCatsView.as_view(), name='add-descriptive-cats'),
    path('get_gcats/',views.GetAllGcats.as_view()),
    path('get_dcats/',views.GetAllDcats.as_view()),
    path('edit_dcats/',views.EditDcats.as_view()),
    path('edit_gcats/',views.EditGcats.as_view()),
    path('get_pgcats/',views.GetAllGcats.as_view()),
    
    path('add_buisness/',views.add_buisness_from_admin),
    

]