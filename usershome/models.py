from django.db import models
from mongodb import db
from django.contrib.auth.models import AbstractUser


# Mongo DB Collections:-

catalogue = db['catalogue']



# Django Models:-

class Extended_User(AbstractUser):
    mobile_number   = models.CharField(max_length=15, null=True, blank=True)

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


    def __str__(self):
        return self.cat_name


# ==========================================================================================


class Popular_General_Cats(models.Model):
    general_cat     = models.ForeignKey(General_cats , on_delete=models.CASCADE)
    



class City (models.Model):
    city_name       = models.CharField(max_length=100 , blank=True)
    
    def __str__(self):
        return self.city_name


    

class Locality (models.Model):
    locality_name   = models.CharField(max_length=100 , blank=True)
    city            = models.ForeignKey(City , on_delete=models.CASCADE)

    def __str__(self):
        return self.locality_name


# ==========================================================================================
    
class Buisnesses(models.Model):
    user                        = models.ForeignKey(Extended_User , on_delete=models.CASCADE , null=True)
    name                        = models.CharField(max_length=100)
    description                 = models.CharField(max_length=1000 , blank=True , null=True)
    buisness_type               = models.CharField(max_length=50)
    manager_name                = models.CharField(max_length=100 , blank=True) 
    building_name               = models.CharField(max_length=50 , blank=True , null=True)
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
    score                       = models.CharField(max_length=12 , default='0' ,)
    image                       = models.ImageField(upload_to='Profile_pics/' ,default='')
    sa_rate                     = models.CharField(max_length=12 , default='15' ,)
    no_of_enquiries             = models.IntegerField(default=0 , blank=True)  
    no_of_views                 = models.IntegerField(default=0 , blank=True)
    


    def __str__(self):
        return self.name
    

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
   
    image           = models.ImageField(upload_to='Home_pics/' , default='' , null=True , blank=True )
    name             = models.ForeignKey(General_cats , on_delete=models.CASCADE)
    title           = models.ForeignKey(Home_Titles , on_delete=models.CASCADE)

class Home_Popular_Des_Cats (models.Model):
   
    # image           = models.ImageField(upload_to='Home_pics/' , default='' , null=True , blank=True )
    name             = models.ForeignKey(Descriptive_cats , on_delete=models.CASCADE)
    title           = models.ForeignKey(Home_Titles , on_delete=models.CASCADE)

class Home_Popular_Product_Cats (models.Model): 
   
    image           = models.ImageField(upload_to='Home_pics/' , default='' , null=True , blank=True )
    name             = models.ForeignKey(Product_Sub_category , on_delete=models.CASCADE)
    title           = models.ForeignKey(Home_Titles , on_delete=models.CASCADE)


class Home_Popular_Cities (models.Model):
   
    image           = models.ImageField(upload_to='Home_pics/' , default='' , null=True , blank=True )
    name             = models.ForeignKey(City , on_delete=models.CASCADE)
    title           = models.ForeignKey(Home_Titles , on_delete=models.CASCADE)
    
    
    
    

# class HomeTitles (models.Model):

#     title           = models.CharField(max_length=70)
#     title_name      = models.CharField(max_length=70)

# class HomeContents (models.Model):
   
#     image           = models.ImageField(upload_to='Home_pics/' , default='' , null=True , blank=True )
#     title           = models.ForeignKey(HomeTitles , on_delete=models.CASCADE)
#     head            = models.CharField(max_length=70)
#     body            = models.CharField(max_length=70)
#     footer          = models.CharField(max_length=70)
    