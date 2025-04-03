from django.db import models
from django.contrib.auth.models import AbstractUser


# Mongo DB Collections:-


       

# Django Models:-




class Plans(models.Model):
    plan_name                                   = models.CharField(max_length=100)
    # trier 1
    profile_visit                               = models.BooleanField(default=False)
    search_priority_1                           = models.BooleanField(default=False)
    image_gallery                               = models.BooleanField(default=False)
    contact_info                                = models.BooleanField(default=False)
    google_map                                  = models.BooleanField(default=False)
    whatsapp_chat                               = models.BooleanField(default=False)
    call_action_button                          = models.BooleanField(default=False)
    bi_analytics                                = models.BooleanField(default=False)
    profile_sharing_URL                         = models.BooleanField(default=False)
    profile_view_count                          = models.BooleanField(default=False)
    profile_social_media_URL_links              = models.BooleanField(default=False)
    social_media_welcome_promotion_in_BI        = models.BooleanField(default=False)
    # tier 2
    search_priority_2                         = models.BooleanField(default=False)
    video_gallery                               = models.BooleanField(default=False)
    posters_6                                   = models.BooleanField(default=False)
    email_id                                    = models.BooleanField(default=False)
    reviews_ratings                             = models.BooleanField(default=False)
    audio_video_ad                              = models.BooleanField(default=False)
    bi_verification                             = models.BooleanField(default=False)
    products_and_service_visibility             = models.BooleanField(default=False)
    social_media_paid_promotion_in_bi_youtube   = models.BooleanField(default=False)
    # tier 3
    search_priority_3                         = models.BooleanField(default=False)
    posters_12                                  = models.BooleanField(default=False)
    todays_offer                                = models.BooleanField(default=False)
    job_portal                                  = models.BooleanField(default=False)
    reels_video_ad                              = models.BooleanField(default=False)
    bi_assured                                    = models.BooleanField(default=False)
    bi_certification                            = models.BooleanField(default=False)
    social_media_paid_promotion_in_bi_12_posters_monthly = models.BooleanField(default=False)



class Extended_User(AbstractUser):
    mobile_number   = models.CharField(max_length=15, null=True, blank=True)
    is_customer     = models.BooleanField(default=False)
    is_vendor       = models.BooleanField(default=False)
    is_admin        = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username

# ==========================================================================================


class General_cats (models.Model):                                                             
    cat_name        = models.CharField(max_length=50 , blank=True)    
    
    
    def __str__(self):
        return self.cat_name


class Descriptive_cats (models.Model):
    cat_name        = models.CharField(max_length=100 , blank=True)
    general_cat     = models.ForeignKey(General_cats , on_delete=models.CASCADE)
    maped           = models.BooleanField(default=False)


    def __str__(self):
        return self.cat_name


# ==========================================================================================


class Popular_General_Cats(models.Model):
    general_cat     = models.ForeignKey(General_cats , on_delete=models.CASCADE)
    



class City (models.Model):
    city_name       = models.CharField(max_length=100 , blank=True)
    maped           = models.BooleanField(default=False)
    
    def __str__(self):
        return self.city_name


    

class Locality (models.Model):
    locality_name   = models.CharField(max_length=100 , blank=True)
    city            = models.ForeignKey(City , on_delete=models.CASCADE)

    def __str__(self):
        return self.locality_name


# ==========================================================================================
    
class Buisnesses(models.Model):
    # Allowing null=True for cases where a business might not be linked to a user initially.
    plan                        = models.ForeignKey(Plans ,on_delete=models.CASCADE , null=True ,blank=True)
    search_priority             = models.IntegerField(default=0)
    user                        = models.ForeignKey(Extended_User , on_delete=models.CASCADE , null=True)
    name                        = models.CharField(max_length=100)
    description                 = models.CharField(max_length=1000 , blank=True , null=True)
    buisness_type               = models.CharField(max_length=50)
    manager_name                = models.CharField(max_length=100 , blank=True) 
    building_name               = models.CharField(max_length=50 , blank=True , null=True)
    landmark                    = models.CharField(max_length=50 , blank=True , null=True)
    locality                    = models.ForeignKey(Locality , on_delete=models.CASCADE)
    city                        = models.ForeignKey(City , on_delete=models.CASCADE , null=True , blank=True)
    state                       = models.CharField(max_length=50 , blank=False , null=False)
    pincode                     = models.CharField(max_length=10 ,blank=True)
    latittude                   = models.CharField(max_length=30 , blank=True)
    longitude                   = models.CharField(max_length=30 , blank=True)
    opens_at                    = models.TimeField(blank=True , null=True)
    closes_at                   = models.TimeField(blank=True , null=True)
    since                       = models.DateField(blank=True , null=True)
    instagram_link              = models.CharField(max_length=100 , blank=True)    
    facebook_link               = models.CharField(max_length=100 , blank=True)    
    x_link                      = models.CharField(max_length=100 , blank=True)    
    youtube_link                = models.CharField(max_length=100 , blank=True)    
    web_link                    = models.CharField(max_length=100 , blank=True) 
    whatsapp_number             = models.CharField(max_length=100 , blank=True)  
    email                       = models.EmailField(max_length=40 , blank=True)  
    incharge_number             = models.CharField(max_length=15 , blank=True)
    maped                       = models.BooleanField(default=False) 
    score                       = models.CharField(max_length=12 , default='0' ,)
    image                       = models.ImageField(upload_to='Profile_pics/' ,default='')
    searched                    = models.IntegerField(default=0)
    no_of_enquiries             = models.IntegerField(default=0 , blank=True)  
    no_of_views                 = models.IntegerField(default=0 , blank=True)
    verified                    = models.BooleanField(default=False)
    assured                     = models.BooleanField(default=False)    
    rating                      = models.FloatField(default=0)    
    total_no_of_ratings         = models.IntegerField(default=0)


    def __str__(self):
        return self.name
    
    
    

    
class BuisnessVisitTracker(models.Model):
    buisness                    = models.ForeignKey(Buisnesses , on_delete=models.CASCADE)
    date                        = models.DateField(auto_now_add=True)
    user                        = models.ForeignKey(Extended_User , on_delete=models.CASCADE , null=True)


class Buisness_Offers(models.Model):
    buisness                = models.ForeignKey(Buisnesses , on_delete = models.CASCADE)
    offer                   = models.IntegerField(default = 0 , blank = False)
    is_percent              = models.BooleanField(default = False)
    is_flat                 = models.BooleanField(default = False)
    minimum_bill_amount     = models.IntegerField(blank = True)
    valid_upto              = models.DateField(blank=True)    
    



class Buisness_pics(models.Model):
    image             = models.ImageField(upload_to='Photo_gallery/' , default='')
    buisness          = models.ForeignKey(Buisnesses , on_delete=models.CASCADE)
    
    
class BuisnessTracker(models.Model):
    buisness                    = models.ForeignKey(Buisnesses , on_delete=models.CASCADE)
    time_spend                  = models.CharField(max_length=50 , default='0' ,)
    date                        = models.DateField( auto_now=True)
 



class Buisness_Descriptive_cats (models.Model):
    dcat            = models.ForeignKey(Descriptive_cats , on_delete=models.CASCADE)
    buisness        = models.ForeignKey(Buisnesses , on_delete=models.CASCADE)
    
    def __str__(self):
        return self.dcat.cat_name
    
    
    
    
class Buisness_General_cats (models.Model):
    gcat            = models.ForeignKey(General_cats , on_delete=models.CASCADE)
    buisness        = models.ForeignKey(Buisnesses , on_delete=models.CASCADE)

     
    def __str__(self):
        return self.gcat.cat_name

# ===========================================================================================

   
class Product_General_category(models.Model):
    cat_name        = models.CharField(max_length=50)
    
    def __str__(self):
        return self.cat_name
   
class Product_Sub_category(models.Model):
    cat_name        = models.CharField(max_length=50)
    general_cat     = models.ForeignKey(Product_General_category , on_delete=models.CASCADE)    
    
    
    def __str__(self):
        return self.cat_name

class Products(models.Model):
    name            = models.CharField(max_length=200 , blank=True)
    price           = models.CharField(max_length=20 , blank=True)
    sub_cat         = models.ForeignKey(Product_Sub_category , on_delete=models.CASCADE)
    description     = models.CharField(max_length=200 , blank=True)
    buisness        = models.ForeignKey(Buisnesses , on_delete=models.CASCADE)
    searched        =  models.IntegerField(default=0 , blank=True)

    
    def __str__(self):
        return self.name


class Product_linked_sub_category(models.Model):
    category        = models.ForeignKey(Product_Sub_category , on_delete=models.CASCADE)
    product         = models.ForeignKey(Products , on_delete=models.CASCADE)
    


class Product_pics(models.Model):
    image             = models.ImageField(upload_to='Product_pics/' , default='')
    product         = models.ForeignKey(Products , on_delete=models.CASCADE)
 
    
# ===========================================================================================


class Service_Cats(models.Model):
    cat_name        = models.CharField(max_length=50)
    buisness        = models.ForeignKey(Buisnesses , on_delete=models.CASCADE)
    
    def __str__(self):
        return self.cat_name
    
    
class Services (models.Model):
    name            = models.CharField(max_length=70)
    price           = models.CharField(max_length=30)
    image           = models.ImageField(upload_to='Sevices_pics/' , default='' , null=True , blank=True )
    cat             = models.ForeignKey(Service_Cats , on_delete=models.CASCADE)
    buisness        = models.ForeignKey(Buisnesses , on_delete=models.CASCADE)
    searched        =  models.IntegerField(default=0 , blank=True)

    def __str__(self):
        return self.name

    
    
    
    
    
    
    
    
# ====================================================================================================================

# Home page datas   

class Home_Titles (models.Model):
    name            = models.CharField(max_length=70)   
    title           = models.CharField(max_length=70)

    def __str__(self):
        return self.title   

    
    

class Home_Popular_General_Cats (models.Model):
   
    image           = models.ImageField(upload_to = 'Home_pics/' , default='' , null = True , blank = True )
    name            = models.ForeignKey(General_cats , on_delete = models.CASCADE)
    title           = models.ForeignKey(Home_Titles , on_delete = models.CASCADE)

class Home_Popular_Des_Cats (models.Model):
   
    # image           = models.ImageField(upload_to='Home_pics/' , default='' , null=True , blank=True )
    name            = models.ForeignKey(Descriptive_cats , on_delete = models.CASCADE)
    title           = models.ForeignKey(Home_Titles , on_delete = models.CASCADE)

class Home_Popular_Product_Cats (models.Model): 
   
    image           = models.ImageField(upload_to = 'Home_pics/' , default='' , null = True , blank = True )
    name            = models.ForeignKey(Product_Sub_category , on_delete = models.CASCADE)
    title           = models.ForeignKey(Home_Titles , on_delete = models.CASCADE)


class Home_Popular_Cities (models.Model):
   
    image           = models.ImageField(upload_to = 'Home_pics/' , default = '' , null = True , blank = True )
    name            = models.ForeignKey(City , on_delete = models.CASCADE)
    title           = models.ForeignKey(Home_Titles , on_delete = models.CASCADE)
    
    
class Home_Meta_data (models.Model):
   
    meta_title             = models.CharField(max_length=400 , null=True)
    meta_description       = models.CharField(max_length=400 , null=True)
    meta_keywords          = models.CharField(max_length=400 , null=True)
    meta_author            = models.CharField(max_length=400 , null=True)
    page_title             = models.CharField(max_length=400 , null=True)
    meta_og_title          = models.CharField(max_length=400 , null=True)
    meta_og_description    = models.CharField(max_length=400 , null=True)
    meta_og_image          = models.ImageField(upload_to='Home_pics/' , default='' , null=True , blank=True )
    meta_og_url            = models.CharField(max_length=400 , null=True)
    meta_og_type           = models.CharField(max_length=400 , null=True)
    meta_og_site_name      = models.CharField(max_length=400 , null=True)
    meta_og_locale         = models.CharField(max_length=400 , null=True)
    meta_og_image_width    = models.CharField(max_length=400 , null=True)
    meta_og_image_height   = models.CharField(max_length=400 , null=True)
    meta_og_image_alt      = models.CharField(max_length=400 , null=True)
    
    
    
class Home_Ads(models.Model):
    name    = models.CharField(max_length=100)
    banner   = models.ImageField(upload_to = 'Home_Ad_Banners/' , default='' , null = True , blank = True )
    

# class HomeTitles (models.Model):

#     title           = models.CharField(max_length=70)
#     title_name      = models.CharField(max_length=70)

# class HomeContents (models.Model):
   
#     image           = models.ImageField(upload_to='Home_pics/' , default='' , null=True , blank=True )
#     title           = models.ForeignKey(HomeTitles , on_delete=models.CASCADE)
#     head            = models.CharField(max_length=70)
#     body            = models.CharField(max_length=70)
#     footer          = models.CharField(max_length=70)
    
    
    
    
    
    
#=============================================================================================================================

# users liked Buisnesses

class Liked_Buisnesses_Group(models.Model):
    name = models.CharField(max_length=70)
    user = models.ForeignKey('Extended_User', on_delete=models.CASCADE, related_name='business_groups')

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Liked_Buisnesses(models.Model):
    buisness = models.ForeignKey('Buisnesses', on_delete=models.CASCADE, related_name='liked_by_groups')
    group = models.ForeignKey('Liked_Buisnesses_Group', on_delete=models.CASCADE, related_name='liked_buisnesses')
    user = models.ForeignKey('Extended_User', on_delete=models.CASCADE , default=None)
    
    class Meta:
        unique_together = ('buisness', 'group')  
        verbose_name = 'Liked Buisness'
        verbose_name_plural = 'Liked Buisnesses'

    def __str__(self):
        return f"{self.buisness.name} in {self.group.name}"





#=======================================================================================



# SEO


class Sitemap_Links(models.Model):
    link                    = models.CharField(max_length=600 ,null=True)
    share_link              = models.CharField(max_length=100 ,null=True)
    single_buisness         = models.BooleanField(default=False)
    cc_combination          = models.BooleanField(default=False)
    city                    = models.ForeignKey(City , on_delete=models.CASCADE , null=True)
    dcat                    = models.ForeignKey(Descriptive_cats , on_delete=models.CASCADE , null=True)
    city_name               = models.CharField(max_length=100, null=True, db_index=True)  # Indexed
    dcat_name               = models.CharField(max_length=100, null=True, db_index=True)  # Indexed
    buisness                = models.ForeignKey(Buisnesses , on_delete=models.CASCADE , null=True ,related_name="sitemap_link")
    meta_title              = models.CharField(max_length=400 , null=True)
    meta_description        = models.CharField(max_length=400 , null=True)
    meta_keywords           = models.CharField(max_length=400 , null=True)
    meta_author             = models.CharField(max_length=400 , null=True)
    meta_og_title           = models.CharField(max_length=400 , null=True)
    meta_og_description     = models.CharField(max_length=400 , null=True)
    meta_og_image           = models.ImageField(upload_to='Home_pics/' , default='' , null=True , blank=True )
    meta_og_url             = models.CharField(max_length=400 , null=True)
    meta_og_site_name       = models.CharField(max_length=400 , null=True)
    page_title              = models.CharField(max_length=400 , null=True)
    last_mod                = models.DateField( auto_now=True)
    change_freq             = models.CharField(max_length=50 , null=True)
    priority                = models.FloatField(default=0.5)    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['city', 'dcat'], name='unique_city_dcat')
        ]
        indexes     = [
            models.Index(fields=["city_name", "dcat_name"]),    
        ]
   
   
    # def __str__(self):
    #     if self.buisness:
    #         return self.buisness.name 
    #     else:   
    #         return self.city.city_name + ' - ' + self.dcat.cat_name

    # def __str__(self):
    #     return 'hello'+str(self.id)+self.link







# ================================

# class Keywords(models.Model):
#     keyword         = models.CharField(max_length=200)
#     dcat            = models.ForeignKey(Descriptive_cats , on_delete=models.CASCADE , null=True)
    




# ================================

class Enquiries (models.Model):
    name            = models.CharField(max_length=50)
    mobile_number   = models.CharField(max_length=15)
    message         = models.CharField(max_length=500 , null=True , blank= True)
    buisness        = models.ForeignKey(Buisnesses , on_delete=models.CASCADE)
    user            = models.ForeignKey(Extended_User , on_delete=models.CASCADE , null=True)
    date            = models.DateField(auto_now=True)
    time            = models.TimeField(auto_now=True)
    is_read         = models.BooleanField(default=False)
        
    def __str__(self):
        return f'{self.name} , {self.mobile_number} , {self.buisness}'

# ===============================

class Reviews_Ratings(models.Model):
    buisness        = models.ForeignKey(Buisnesses , on_delete=models.CASCADE)
    user            = models.ForeignKey(Extended_User , on_delete=models.CASCADE)
    review          = models.CharField(max_length=500 , null=True , default='')
    rating          = models.IntegerField(default=0 )
    date            = models.DateField(auto_now=True)
    time            = models.TimeField(auto_now=True)
    def __str__(self):
        return f'{self.buisness} , {self.user} , {self.review}'
    
class Review_pics(models.Model):
    image           = models.ImageField(upload_to='Review_pics/' , default='')
    review          = models.ForeignKey(Reviews_Ratings , on_delete=models.CASCADE)
    
    
    
    
# -------------------------------------------------------------------------------


class Auth_OTPs(models.Model):
    otp             = models.IntegerField()
    phone           = models.CharField(max_length=11 )
    name            = models.CharField(max_length=60 , null= True)
    exists          = models.BooleanField(default=False)
    enquiry         = models.CharField(max_length=500 , null=True)
class Email_OTPs(models.Model):
    otp             = models.IntegerField()
    email           = models.CharField(max_length=100 )
    bid             = models.CharField(max_length=50, null=True)