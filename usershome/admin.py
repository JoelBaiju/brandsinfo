from django.contrib import admin
from .models import *
from django.contrib.auth.models import User  # Import default User model


class dcatsAdmin(admin.ModelAdmin):
    list_display = ('id', 'cat_name', 'general_cat')  

class cityAdmin(admin.ModelAdmin):
    list_display = ('id', 'city_name')  



class ExtendedUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'is_customer', 'is_vendor') 

    def display_name(self, obj):
       
        return obj.first_name

    display_name.short_description = 'Name' 

admin.site.register(Extended_User, ExtendedUserAdmin)




class site_links_Admin(admin.ModelAdmin):
    list_display = ['id','name', 'price', 'cat']


admin.site.register( Descriptive_cats,dcatsAdmin)
admin.site.register( City,cityAdmin)


admin.site.register(Buisness_Descriptive_cats)
admin.site.register(Buisness_General_cats)
admin.site.register(General_cats)
admin.site.register(Buisness_Offers)
# admin.site.register(Descriptive_cats)
admin.site.register(Product_General_category)
admin.site.register(Product_Sub_category)
admin.site.register(Product_pics)
admin.site.register(Products)
# admin.site.register(City)
admin.site.register(Locality)
admin.site.register(Services)
admin.site.register(Service_Cats)
admin.site.register(Popular_General_Cats)
admin.site.register(Home_Titles)
admin.site.register(Home_Popular_Cities)
admin.site.register(Home_Popular_Des_Cats)
admin.site.register(Home_Popular_General_Cats)
admin.site.register(Home_Popular_Product_Cats)
admin.site.register(Home_Meta_data)
admin.site.register(Liked_Buisnesses)
admin.site.register(Liked_Buisnesses_Group)
admin.site.register(Product_linked_sub_category)
admin.site.register(Reviews_Ratings)
admin.site.register(Review_pics)
admin.site.register(Home_Ads)
admin.site.register(Auth_OTPs)
admin.site.register(BuisnessVisitTracker)
    
    
admin.site.register(Buisness_keywords)
admin.site.register(Keywords)



class PlansAdmin(admin.ModelAdmin):
    list_display = ['id', 'plan_name']
    
class plan_varientsAdmin(admin.ModelAdmin):
    list_display = ['id', 'plan' , 'price']

class BuisnessVideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'buisness']

admin.site.register(Buisness_Videos , BuisnessVideoAdmin)
    
admin.site.register(Plans , PlansAdmin)

admin.site.register(Plan_Varients , plan_varientsAdmin)
    

class ProductsAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'cat']
    search_fields = ['name', 'cat__cat_name']
    
    

class BuisnessesAdmin(admin.ModelAdmin):
    list_display = ['id','name']
    
admin.site.register(Buisnesses ,BuisnessesAdmin)

class SitemaplinksAdmin(admin.ModelAdmin):
    list_display = ['id','link']
    
admin.site.register(Sitemap_Links , SitemaplinksAdmin)


class TransactionsAdmin(admin.ModelAdmin):
    list_display = ['order_id','user','amount','status','buisness','transction_id','phonepe_order_id']
    
admin.site.register(PhonePeTransaction , TransactionsAdmin)

class BuisnessPicsAdmin(admin.ModelAdmin):
    list_display = ['id','buisness']
admin.site.register(Buisness_pics,BuisnessPicsAdmin)
