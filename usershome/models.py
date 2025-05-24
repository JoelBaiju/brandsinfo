from django.db import models
from django.contrib.auth.models import AbstractUser


# Mongo DB Collections:-


       

# Django Models:-



class Plans(models.Model):
    plan_name                                   = models.CharField(max_length=100)
    verbouse_name                               = models.CharField(max_length=100,default='')
    # trier 1
    business_hours                              = models.BooleanField(default=False)
    review_ratings                              = models.BooleanField(default=False)
    social_meida                                = models.BooleanField(default=False)
    offers                                      = models.BooleanField(default=False)    
    enquiry                                     = models.BooleanField(default=False)
    call                                        = models.BooleanField(default=False)
    
    profile_visit                               = models.BooleanField(default=False)
    average_time_spend                          = models.BooleanField(default=False)
    chat                                        = models.BooleanField(default=False)
    search_priority_1                           = models.BooleanField(default=False)
    image_gallery                               = models.BooleanField(default=False)
    google_map                                  = models.BooleanField(default=False)
    whatsapp_chat                               = models.BooleanField(default=False)
    profile_view_count                          = models.BooleanField(default=False)
    # tier 2
    sa_rate                                     = models.BooleanField(default=False)
    keywords                                    = models.BooleanField(default=False)
    search_priority_2                           = models.BooleanField(default=False)
    video_gallery                               = models.BooleanField(default=False)
    bi_verification                             = models.BooleanField(default=False)
    products_and_service_visibility             = models.BooleanField(default=False)
    social_media_paid_promotion_in_bi_youtube   = models.BooleanField(default=False)
    # tier 3
    most_searhed_p_s                            = models.BooleanField(default=False)
    search_priority_3                           = models.BooleanField(default=False)
    todays_offer                                = models.BooleanField(default=False)
    bi_assured                                  = models.BooleanField(default=False)
    bi_certification                            = models.BooleanField(default=False)
    
    def __str__(self):
        return self.plan_name
    
    
    

class Plan_Varients(models.Model):
    plan            = models.ForeignKey(Plans ,related_name='varients', on_delete=models.CASCADE)
    duration        = models.CharField(max_length=50)
    price           = models.CharField(max_length=50)
    
    def __str__(self):
        return self.plan.plan_name + ' - ' + self.duration + ' - ' + self.price
    

class Extended_User(AbstractUser):
    mobile_number   = models.CharField(max_length=15, null=True, blank=True)
    is_customer     = models.BooleanField(default=False)
    is_vendor       = models.BooleanField(default=False)
    is_admin        = models.BooleanField(default=False)
    device_id    = models.CharField(max_length=255, null=True, blank=True)
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
    plan_variant                = models.ForeignKey(Plan_Varients , on_delete=models.CASCADE , null=True , blank=True)
    plan_start_date             = models.DateField(auto_now_add=True , null=True , blank=True)
    plan_expiry_date            = models.DateField(null=True , blank=True)
    search_priority             = models.IntegerField(default=0)
    user                        = models.ForeignKey(Extended_User , on_delete=models.CASCADE , null=True)
    name                        = models.CharField(max_length=100)
    created_on                  = models.DateField(auto_now_add=True ,null=True)
    description                 = models.CharField(max_length=1000 , blank=True , null=True)
    buisness_type               = models.CharField(max_length=50)
    manager_name                = models.CharField(max_length=100 , blank=True) 
    building_name               = models.CharField(max_length=2000 , blank=True , null=True)
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





    
    
class Keywords(models.Model):
    keyword         = models.CharField(max_length=200)
    
    def __str__(self):
        return self.keyword
    
    
class Buisness_keywords(models.Model):
    keyword         = models.ForeignKey(Keywords , on_delete=models.CASCADE)
    buisness        = models.ForeignKey(Buisnesses , on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.id) + ' - ' + self.keyword.keyword + ' - ' + self.buisness.name
    
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
    is_active               = models.BooleanField(default=True)
    



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
    general_cat     = models.ForeignKey(Product_General_category , on_delete=models.CASCADE ,related_name='subcats')     
    
    
    def __str__(self):
        return self.cat_name

class Products(models.Model):
    name            = models.CharField(max_length=200 , blank=True)
    price           = models.CharField(max_length=20 , blank=True)
    sub_cat         = models.ForeignKey(Product_Sub_category , on_delete=models.CASCADE)
    description     = models.CharField(max_length=200 , blank=True)
    buisness        = models.ForeignKey(Buisnesses ,related_name='products', on_delete=models.CASCADE)
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
    description     = models.CharField(max_length=200 , blank=True , null=True)
    cat             = models.ForeignKey(Service_Cats , on_delete=models.CASCADE)
    buisness        = models.ForeignKey(Buisnesses ,related_name='services', on_delete=models.CASCADE)
    searched        =  models.IntegerField(default=0 , blank=True)

    def __str__(self):
        return self.name



class Service_pics(models.Model):
    image             = models.ImageField(upload_to='Sevices_pics/' , default='')
    service         = models.ForeignKey(Services , on_delete=models.CASCADE)
 

    
    
    
    
    
    
    
    
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
    otp             = models.CharField(max_length=20)
    phone           = models.CharField(max_length=11 )
    name            = models.CharField(max_length=60 , null= True)
    exists          = models.BooleanField(default=False)
    enquiry         = models.CharField(max_length=500 , null=True)
    
class Email_OTPs(models.Model):
    otp             = models.CharField(max_length=20)
    email           = models.CharField(max_length=100 )
    bid             = models.CharField(max_length=50, null=True)
    
    
    
# ================================================================================

class Buisness_Videos(models.Model):
    video_file = models.FileField(upload_to='Buisness_Videos/')
    buisness   = models.ForeignKey(Buisnesses, on_delete=models.CASCADE, related_name='buisness_videos')
    is_converted = models.BooleanField(default=False)
    hls_path = models.CharField(max_length=255, blank=True, null=True)  # optional
    



# ================================================================================


# class Search_history(models.Model):
#     keyword = models.CharField(max_length=100)
#     user    = models.ForeignKey(Extended_User , null=True , blank=True , on_delete=models.CASCADE)
#     location = models.CharField(max_length=100)
#     # matched_cats = models.


# ================================================================================

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class PhonePeTransaction(models.Model):
    class TransactionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        INITIATED = 'INITIATED', 'Initiated'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        EXPIRED = 'EXPIRED', 'Expired'
        REFUNDED = 'REFUNDED', 'Refunded'
        PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED', 'Partially Refunded'

    order_id                    = models.CharField(max_length=100, unique=True, verbose_name="Transaction ID",)
    user                        = models.ForeignKey('Extended_User', on_delete=models.CASCADE, related_name='phonepe_transactions', verbose_name="User" , null=True )
    amount                      = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)], verbose_name="Amount (₹)", )
    status                      = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    phonepe_response            = models.JSONField(null=True, blank=True, verbose_name="PhonePe Response")
    phonepe_callback            = models.JSONField(null=True, blank=True, verbose_name="Callback Data")
    payment_url                 = models.URLField(null=True, blank=True, max_length=500, verbose_name="Payment URL")
    created_at                  = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at                  = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    expire_at                   = models.DateTimeField(null=True, blank=True, verbose_name="Expiration Time")
    buisness                    = models.ForeignKey('Buisnesses', on_delete=models.CASCADE, null=True, blank=True, related_name='transactions', verbose_name="Business")
    plan                        = models.ForeignKey('Plans', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name="Subscription Plan")
    plan_variant                = models.ForeignKey(Plan_Varients , on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name="Plan Variant")
    payment_completed_at        = models.DateTimeField(null=True, blank=True, verbose_name="Payment Completed At")
    phonepe_order_id            = models.CharField(max_length=100, null=True, blank=True, verbose_name="PhonePe Order ID" )
    transction_id               = models.CharField(max_length=100, null=True, blank=True, verbose_name="Transaction ID")
    payment_mode                = models.CharField(max_length=50, null=True, blank=True, verbose_name="Payment Mode")
    invoice                     = models.FileField(upload_to='invoices/', null=True, blank=True, verbose_name="Invoice")
    class Meta:
      
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['buisness']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gte=0.01), name="amount_gte_0"),
        ]

    def __str__(self):
        return f"{self.user} - {self.order_id} - {self.get_status_display()} - ₹{self.amount}"

    def save(self, *args, **kwargs):
        if self.status == self.TransactionStatus.SUCCESS and not self.payment_completed_at:
            self.payment_completed_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_successful(self): return self.status == self.TransactionStatus.SUCCESS

    @property
    def duration_days(self): return self.plan_variant.duration_days if self.plan_variant else None

    def mark_as_refunded(self, partial=False):
        self.status = self.TransactionStatus.PARTIALLY_REFUNDED if partial else self.TransactionStatus.REFUNDED
        self.save(update_fields=['status', 'updated_at'])