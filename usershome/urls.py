from django.contrib import admin
from django.urls import path
from . import views
from . import auth_views
from . import sitemap_view
from .e_searcher import elasticsearch2 , keyword_suggestions
urlpatterns = [
    
# ========================== Add buisness urls

    path('getlocality/',views.get_locality_with_city),
    path('buisnesses/',views.BuisnessesView.as_view()),
    path('buisnesses_short/',views.BuisnessesShortView.as_view()),
    path('buisnessesedit/<int:pk>/',views.BuisnessesEdit.as_view()),
    path('buisnesses_na/',views.BuisnessesView_for_customers.as_view()),
    path('buisness_pics/',views.BuisnessImages.as_view()),
    path('delete_pic/<int:pk>/', views.BuisnessPics_Delete.as_view()),
    path('offers/add/', views.AddOfferView.as_view(), name='add-offer'),
    path('offers/delete/<int:id>/', views.DeleteOfferView.as_view(), name='delete-offer'),
    path('offers/', views.GetOffersView.as_view(), name='offers'),
    path('addlocation/',views.Get_location_view),
    
# ========================== Auth urls

    path('signup1/',auth_views.signup_request_1),
    
    path('verifyotp_customers/',auth_views.verifyotp_customers),
    path('verifyotp/',auth_views.verifyotp_buisnesses),
    path('verifyotp_e/',auth_views.verifyotp_from_enquiry),    
    path('signup2/',auth_views.signup_request_2),
    path('resendotp/',auth_views.resendotp),
    
    
    
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
    
    path('addemail/',views.addemail),
    path('resendemailotp/',views.resendemailotp),
    path('verifyemailotp/',views.verifyemailotp),
    # path('search/',views.search),
    
    
    
#  ========================= Users URLs
    
    path('esearch/', elasticsearch2),
    path('suggestions/', keyword_suggestions),
    path('tracktime/',views.tracker_addtime),

    path('home/',views.HomeView),
    
    path('groups/', views.Create_Group_View.as_view(), name='create-group'), 
    path('groups/user/', views.User_Groups_View.as_view(), name='user-groups'), 
    path('groups/add-business/', views.Add_Liked_Buisnesses_to_group.as_view(), name='add-business-to-group'),
    
    path('check_bookmarked/', views.check_bookmarked),
    path('enquiries/', views.Enquiries_View.as_view()),
    
    path('reviews/add/', views.Reviews_Ratings_View.as_view()),
    path('reviews/', views.Get_Reviews_Ratings_View.as_view()),




# ========================== SEO SiteMapping

    path('alpha/sitemap_generator_allatonce_SB/', sitemap_view.Site_Map_Generator_ALLATONCE_SB),
    path('alpha/sitemap_generator_allatonce_CC/', sitemap_view.Site_Map_Generator_ALLATONCE_CC),
    
]