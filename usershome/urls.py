from django.contrib import admin
from django.urls import path
from . import views
 
urlpatterns = [
    path('getlocality/',views.get_locality_with_city),
    path('buisnesses/',views.BuisnessesView.as_view()),
    path('signup1/',views.signup_request_1),
    path('verifyotp/',views.verifyotp),
    path('signup2/',views.signup_request_2),
    path('resendotp/',views.resendotp),
    path('searchpcats/',views.search_products_category),
    path('addproduct/', views.AddProductWithImagesView.as_view()),
    path('services/', views.ServiceListCreateView.  as_view()),
    path('servicecats/', views.ServiceCats.as_view()),
    path('search_gencats/', views.search_general_category),    
    path('add_bgencats/', views.add_bg_category),    
    path('get_descats/', views.get_des_category),    
    path('add_descats/',views.add_des_category),
    path('search/',views.search)
]