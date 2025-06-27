from django.contrib import admin
from django.urls import path
from . import views
from . import auth_views



urlpatterns = [
    
    path('login/',auth_views.admin_auth_view),
    path('dash/',views.admin_dashboard_view),   
    path('add_general_cats/', views.AddGeneralCatsView.as_view(), name='add-general-cats'),
    path('add_descriptive_cats/', views.AddDescriptiveCatsView.as_view(), name='add-descriptive-cats'),
    path('get_gcats/',views.GetAllGcats.as_view()),
    path('get_dcats/',views.GetAllDcats.as_view()),
    path('edit_dcats/<int:pk>/',views.EditDcats.as_view()),
    path('edit_gcats/<int:pk>/',views.EditGcats.as_view()),
    
    path('get_p_gcats/',views.GetAllProductGeneralCats.as_view()),
    path('get_p_subcats/',views.GetAllProductSubCats.as_view()),
    path('add_p_subcats/',views.AddProductSubCatsView.as_view()),
    path('add_p_gcats/',views.AddProductGeneralCatsView.as_view()),
    
    
    path('add_buisness/',views.add_buisness_from_admin),
    path('add_user/',views.add_users_from_admin),
    path('get_users/',views.get_users.as_view()),
    path('get_buisnesses/',views.get_buisnesses.as_view()),

    path('add_cities/', views.AddCities.as_view(), name='add_cities'),
    path('add_localities/', views.AddLocalities.as_view(), name='add_localities'),
    
    path('edit_city/<int:id>/'      , views.EditCityAPIView.as_view()),
    path('delete_city/<int:id>/'    , views.DeleteCityAPIView.as_view()),
    
    path('edit_locality/<int:id>/'  , views.EditLocalityAPIView.as_view()),
    path('delete_locality/<int:id>/', views.DeleteLocalityAPIView.as_view()),

    path('add-plan-to-business/', views.add_plan_to_buisness, name='add_plan_to_buisness'),
    path('tune_buisness/', views.business_tune_api, name='business_api'),


    path('buisness_browser/', views.browse_businesses,name='buisness_browser'),
    path('buisness_search/', views.business_search_view, name='business_search'),



]


