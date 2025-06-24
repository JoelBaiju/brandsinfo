from django.contrib import admin
from django.urls import path
from .Views import views
from .Views import auth_views
from .Views import sitemap_view
from .Views import ps_views
from .Ai import cohere
from .SearchEngines.e_searcher import *
from .Views.streaming_views import VideoUploadView
from .Views.payment_view import puchase_plan , pcreds

from communications.draft4sms import senddd
from usershome.Ai.review_generator import GenerateDummyReviews
from usershome.Reviews.review_models import getEgReviews

urlpatterns = [
    
# ========================== Add buisness urls

    path('getlocality/',views.get_locality_with_city),
    path('buisnesses/',views.BuisnessesView.as_view()),
    path('buisnesses_short/',views.BuisnessesShortView.as_view()),
    path('bwithnplan/',views.get_buisnesses_with_no_plan),
    
    path('buisnessesedit/<int:pk>/',views.BuisnessesEdit.as_view()),
    
    path('buisnesses_na/',views.BuisnessesView_for_customers.as_view()),
    path('buisness_pics/',views.BuisnessImages.as_view()),
    path('delete_pic/<int:pk>/', views.BuisnessPics_Delete.as_view()),
    path('offers/add/', views.AddOfferView.as_view(), name='add-offer'),
    path('offers/edit/<int:id>', views.EditOfferView.as_view(), name='Edit-offer'),
    path('offers/delete/<int:id>/', views.DeleteOfferView.as_view(), name='delete-offer'),
    path('offers/', views.GetOffersView.as_view(), name='offers'),
    path('addlocation/',views.Get_location_view),
    
# ========================== Auth urls
    path('userdata/',auth_views.User_Data.as_view()),
    path('signup1/',auth_views.signup_request_1),
    
    path('verifyotp_customers/',auth_views.verifyotp_customers),
    path('verifyotp/',auth_views.verifyotp_buisnesses),
    path('verifyotp_e/',auth_views.verifyotp_from_enquiry),    
    path('signup2/',auth_views.signup_request_2),
    path('resendotp/',auth_views.resendotp),
    
# ========================== 
    
    path('searchpcats/',ps_views.search_products_category),
    path('addproduct/' , ps_views.AddProductWithImagesView.as_view()),
    path('deleteproduct/<int:pk>/', ps_views.ProductDelete.as_view()),
    path('dlt_product_img/<int:pk>/', ps_views.ProductPics_Delete.as_view()),    
    path('edt_product/<int:id>/', ps_views.EditProductView.as_view()),    
    path('add_product_img/', ps_views.Add_product_images.as_view()),    
    
    
    path('services/', ps_views.ServiceListCreateView.as_view()),
    path('deleteservice/<int:pk>/', ps_views.ServiceDelete.as_view()),
    path('servicecats/', ps_views.ServiceCats.as_view()),
    path('dlt_service_img/<int:pk>/', ps_views.ServicePics_Delete.as_view()),    
    path('edt_service/<int:id>/', ps_views.EditServiceView.as_view()),    
    path('add_service_img/', ps_views.Add_Services_images.as_view()),    
    
    
    path('popular_gencats/', views.Popular_general_cats_view.as_view()),    
    path('search_gencats/', keyword_suggestions_for_gcats),    
    path('add_bgencats/', views.add_bg_category),    
    path('get_descats/', views.get_des_category),    
    path('add_descats/',views.add_des_category),
    path('dlt_descats/<int:pk>/',views.Delete_des_category.as_view()),
    path('get_bdcats/' , views.get_bdcats),
    
    path('addemail/',views.addemail),
    path('resendemailotp/',views.resendemailotp),
    path('verifyemailotp/',views.verifyemailotp),
    # path('search/',views.search),
    
    path('plans/',views.get_plans),
    
#  ========================= Users URLs
    
    
    
    
    path('esearch/', elasticsearch2),
    path('suggestions/', keyword_suggestions_for_major_suggestions),
    path('search_users/', search_users),
    path('search_buisnesses/', search_buisnesses),
    path('suggestions_bdcats/', keyword_suggestions_for_bdcats),
    path('suggestions_gcats/', keyword_suggestions_for_gcats),
    path('tracktime/',views.tracker_addtime),

    path('suggestions_cities/'      , keyword_suggestions_for_cities),
    path('suggestions_localities/'  , keyword_suggestions_for_localities),
    path('search_cities/'           , search_cities),
    path('search_localities/'       , search_localities),

    path('home/',views.HomeView),   
    
    path('groups/', views.Create_Group_View.as_view(), name='create-group'), 
    path('groups/user/', views.User_Groups_View.as_view(), name='user-groups'), 
    path('groups/add-business/', views.Add_Liked_Buisnesses_to_group.as_view(), name='add-business-to-group'),
    
    path('check_bookmarked/', views.check_bookmarked),
    path('enquiries/', views.Enquiries_View.as_view()),
    
    path('reviews/add/', views.Reviews_Ratings_View.as_view()),
    path('reviews/', views.Get_Reviews_Ratings_View.as_view()),

    path('add_deviceid/', views.add_device_id),
    
    path('search_p_gcats/', keyword_suggestions_for_Product_gcats),
    path('search_p_sub_cats/', keyword_suggestions_for_Product_sub_cats),



# ========================== SEO SiteMapping

    path('alpha/sitemap_generator_allatonce_SB/', sitemap_view.Site_Map_Generator_ALLATONCE_SB),
    path('alpha/sitemap_generator_allatonce_CC/', sitemap_view.Site_Map_Generator_ALLATONCE_CC),
    path('alpha/sgs_test/', sitemap_view.Site_Map_Generator_SB_single_Test_api),
    # path('alpha/sgs_test/cohere/', cohere.Site_Map_Generator_SB_single_Test_api),
    
        
    
# ========================== Video
    path('uploadvideo/', VideoUploadView.as_view(), name='upload-video'),
    path('deletevideo/<int:pk>/', views.VideoDelete.as_view(), name='delete-video'),
    
    path('notifytest/', puchase_plan, name='p'),

    path('pcreds/',pcreds, name='pcreds'),
    

# =============================
    path('send/' , senddd ),
    path('review/',GenerateDummyReviews.as_view() ),
    path('eg_review/',getEgReviews.as_view()),
    path('kicker_review/', views.KickstartBusinessReviewTracker.as_view())    
    
    
    
    
    
]



