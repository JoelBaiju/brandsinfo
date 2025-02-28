from django.contrib import admin
from django.urls import path
from . import views

 
urlpatterns = [
    path('getlocality/',views.get_locality_with_city),
    path('buisnesses/',views.BuisnessesView.as_view()),
    path('buisnessesedit/<int:pk>/',views.BuisnessesEdit.as_view()),
    path('buisnesses_na/',views.BuisnessesView_for_customers.as_view()),
    path('buisness_pics/',views.BuisnessImages.as_view()),
    path('signup1/',views.signup_request_1),
    path('verifyotp/',views.verifyotp),
    path('signup2/',views.signup_request_2),
    path('resendotp/',views.resendotp),
    path('searchpcats/',views.search_products_category),
    path('addproduct/', views.AddProductWithImagesView.as_view()),
    path('deleteproduct/<int:pk>/', views.ProductDelete.as_view()),
    path('services/', views.ServiceListCreateView.as_view()),
    path('deleteservice/<int:pk>/', views.ServiceDelete.as_view()),
    path('servicecats/', views.ServiceCats.as_view()),
    path('popular_gencats/', views.Popular_general_cats_view.as_view()),    
    path('search_gencats/', views.search_general_category),    
    path('add_bgencats/', views.add_bg_category),    
    path('get_descats/', views.get_des_category),    
    path('add_descats/',views.add_des_category),
    # path('search/',views.search),
    path('esearch/',views.elasticsearch),
    path('tracktime/',views.tracker_addtime),
    path('addemail/',views.addemail),
    path('resendemailotp/',views.resendemailotp),
    path('verifyemailotp/',views.verifyemailotp),
    path('verifyemailotp/',views.verifyemailotp),
    path('home/',views.HomeView),
    
]