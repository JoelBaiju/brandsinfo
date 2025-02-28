from django.contrib import admin
from .models import *

admin.site.register(Buisnesses)
admin.site.register(Buisness_Descriptive_cats)
admin.site.register(Buisness_General_cats)
admin.site.register(General_cats)
admin.site.register(Descriptive_cats)
admin.site.register(Extended_User)
admin.site.register(Product_General_category)
admin.site.register(Product_Sub_category)
admin.site.register(Product_pics)
admin.site.register(Products)
admin.site.register(City)
admin.site.register(Locality)
admin.site.register(Services)
admin.site.register(Popular_General_Cats)
admin.site.register(Home_Titles)
admin.site.register(Home_Popular_Cities)
admin.site.register(Home_Popular_Des_Cats)
admin.site.register(Home_Popular_General_Cats)
admin.site.register(Home_Popular_Product_Cats)



class ProductsAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'cat']
    search_fields = ['name', 'cat__cat_name']