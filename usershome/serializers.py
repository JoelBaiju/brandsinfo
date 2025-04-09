from rest_framework import serializers
from .models import * 



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extended_User
        fields=['mobile_number','first_name']
        

class SiteSaplinksSerializerFull(serializers.ModelSerializer):
    class Meta:
        model = Sitemap_Links
        fields = ['id', 'link', 'single_buisness', 'cc_combination',
                  'city' ,'dcat','buisness','meta_title','meta_description',
                  'meta_keywords','meta_author','page_title','meta_og_image',
                  'meta_og_title','meta_og_description','meta_og_url',
                  'meta_og_site_name','last_mod','priority','change_freq','share_link']
        
class SiteSaplinksSerializerMini(serializers.ModelSerializer):
    class Meta:
        model = Sitemap_Links
        fields = ['id', 'link' ,'meta_keywords']
        


class Popular_general_cats_serializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='general_cat', read_only=True)
    id = serializers.PrimaryKeyRelatedField(source='general_cat', read_only=True)  
    
    class Meta:
        model = Popular_General_Cats
        fields = ['name', 'id']
        


class BuisnessPicsSerializer(serializers.ModelSerializer):
   
    image       = serializers.ImageField()
    
    class Meta:
        model  = Buisness_pics
        fields  = [
                    'id',
                    'image' ,
                  ]




class ReviewPicsSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Review_pics
        fields  = ['image']


class ReviewRatingSerializer(serializers.ModelSerializer):
    buisness = serializers.PrimaryKeyRelatedField(
    queryset=Buisnesses.objects.all(),
    )
    user = serializers.PrimaryKeyRelatedField(
    queryset=Extended_User.objects.all()    
    )   
    name = serializers.StringRelatedField(source='user.first_name', read_only=True)
    image = ReviewPicsSerializer(source='review_pics_set', many=True, read_only=True)

        
    class Meta:
        model = Reviews_Ratings
        fields = ['id', 'rating', 'review', 'buisness', 'date', 'time', 'user' , 'name','image']
        
    
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        review = Reviews_Ratings.objects.create(**validated_data)   
        for image in images_data:
            Review_pics.objects.create(review=review, image=image)  
        return review
    
  



class ReviewRatingSerializerMini(serializers.ModelSerializer):
        
    class Meta:
        model = Reviews_Ratings
        fields = ['id', 'rating']
   
    


class BDescriptiveCatsSerializer(serializers.ModelSerializer):
    cat_name = serializers.SerializerMethodField()

    class Meta:
        model = Buisness_Descriptive_cats
        fields = ['id', 'cat_name']

    def get_cat_name(self, obj):
        return obj.dcat.cat_name


class BGeneralCatsSerializer(serializers.ModelSerializer):
    cat_name = serializers.StringRelatedField(source='gcat.cat_name', read_only=True)
    class Meta:
        model = Buisness_General_cats
        fields = ['id', 'cat_name']




class BuisnessOffersSerializer(serializers.ModelSerializer):
    
    buisness = serializers.PrimaryKeyRelatedField(queryset=Buisnesses.objects.all())
    
    class Meta:
        model = Buisness_Offers
        fields = ['id', 'buisness', 'offer', 'is_percent','is_flat', 'minimum_bill_amount', 'valid_upto']
        extra_kwargs = {
            'buisness': {'required': True},  # Ensure business is always provided
            'offer': {'required': True},      # Ensure offer is always provided
        }

    def create(self, validated_data):
        is_percent = validated_data.get('is_percent', False)
        offer = validated_data.get('offer', 0)

        if is_percent and offer > 100:
            raise serializers.ValidationError("Offer value cannot exceed 100% for percentage-based offers.")
        
        return super().create(validated_data)



class PlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plans
        fields = [
            'plan_name','profile_visit','image_gallery',
            'google_map','whatsapp_chat',
            'profile_view_count',
            'video_gallery',
            'bi_verification','products_and_service_visibility',
            'bi_assured','bi_certification','keywords','average_time_spend',
            'sa_rate'
        ]

class BuisnessesSerializer(serializers.ModelSerializer):
    image       = serializers.ImageField(required=False)
    city        = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    locality    = serializers.PrimaryKeyRelatedField(queryset=Locality.objects.all())
    user        = serializers.PrimaryKeyRelatedField(
                    queryset=Extended_User.objects.all()
                    )
    image_gallery   = BuisnessPicsSerializer(many=True, read_only=True)
    plan = PlansSerializer( read_only=True)

    class Meta:
        model = Buisnesses
        fields=['id','name','description','buisness_type','manager_name',
                'building_name','locality','city','state','pincode',
                'latittude','longitude','opens_at','closes_at',
                'since','no_of_views','instagram_link','facebook_link',
                'web_link','x_link','youtube_link','whatsapp_number',
                'incharge_number','user','score','image',
                'searched',  'no_of_enquiries','email','image_gallery','plan'
                ]
        
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = BuisnessPicsSerializer(
            instance.buisness_pics_set.all(), many=True
        ).data
        return representation
    
    def create(self, validated_data):
        user=validated_data.pop('owner', None)  
        
        return Buisnesses.objects.create(**validated_data)
    
    
    

class BuisnessesSerializerFull(serializers.ModelSerializer):
    image       = serializers.ImageField(required=False)
    city        = serializers.StringRelatedField()
    locality    = serializers.StringRelatedField()
    user        = serializers.PrimaryKeyRelatedField(
                    queryset=Extended_User.objects.all()
                    )
    image_gallery = BuisnessPicsSerializer(many=True, read_only=True)
    plan = PlansSerializer( read_only=True)

    
    class Meta:
        model = Buisnesses
        fields=['id','name', 'description', 'buisness_type', 'manager_name',
                'building_name','locality','city','state','pincode',
                'latittude','longitude','opens_at','closes_at','since',
                'no_of_views','instagram_link','facebook_link','web_link',
                'x_link','youtube_link','whatsapp_number','incharge_number','user',
                'score','image',  'no_of_enquiries','email','image_gallery','plan'
                ]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image_gallery'] = BuisnessPicsSerializer(
            instance.buisness_pics_set.all(), many=True
        ).data
        return representation



class BuisnessesSerializerCustomers(serializers.ModelSerializer):
    image       = serializers.ImageField()
    city        = serializers.StringRelatedField()
    locality    = serializers.StringRelatedField()
    user        = serializers.PrimaryKeyRelatedField(
                    queryset=Extended_User.objects.all()
                    )
    image_gallery   = BuisnessPicsSerializer(many=True, read_only=True)
    site_data       = SiteSaplinksSerializerFull(source='sitemap_link', read_only=True)
    review_rating   = ReviewRatingSerializerMini(source='reviews_ratings_set', many=True, read_only=True)
    plan = PlansSerializer( read_only=True)

    class Meta:
        model   = Buisnesses
        fields  = [ 'id','name','description','buisness_type',
                    'manager_name','building_name','locality','city',
                    'state','pincode','latittude','longitude',
                    'opens_at','closes_at','since','no_of_views',
                    'instagram_link','facebook_link','web_link','x_link',
                    'youtube_link','whatsapp_number','incharge_number','user',
                    'image','image_gallery','site_data','email','verified',
                    'assured','review_rating','rating','plan'
                 ]
    
   
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        plan = instance.plan
        if plan and plan.image_gallery:
            representation['image_gallery'] = BuisnessPicsSerializer(
                instance.buisness_pics_set.all(), many=True
            ).data
        else:
            representation['image_gallery'] = []  # Set to empty if not allowed

        
        sitemap_link = instance.sitemap_link.first() 
        if sitemap_link:
            representation['site_data'] = SiteSaplinksSerializerFull(sitemap_link).data
        else:
            representation['site_data'] = None  
            
        representation['review_rating'] = ReviewRatingSerializerMini(
            instance.reviews_ratings_set.all(), many=True   
        ).data
        
       
        return representation
    

from django.db.models import Avg

class ProductMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'name', 'price' ]

class ServiceMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ['id', 'name', 'price' ,'description']



class BuisnessesSerializerMini(serializers.ModelSerializer):
    image       = serializers.ImageField()        
    city        = serializers.StringRelatedField()
    locality    = serializers.StringRelatedField()
    user        = serializers.PrimaryKeyRelatedField(
                    queryset=Extended_User.objects.all()
                )
    offers      = BuisnessOffersSerializer(many=True, read_only=True)
    redirect_link = SiteSaplinksSerializerMini(source='sitemap_link', read_only=True)
    products = ProductMiniSerializer(many=True, read_only=True)
    services = ServiceMiniSerializer(many=True, read_only=True)
    plan = PlansSerializer( read_only=True)
    class Meta:
        model   = Buisnesses
        fields  = [  
                    'id','search_priority','name','buisness_type','locality',
                    'city','state','no_of_views','user',
                    'score','image','offers','redirect_link','rating',
                    'verified','assured','plan','products','services','building_name','state',
                    'whatsapp_number'
                 ]
    
    
    
    

    def get_filtered_data(self, instances):

        return [instance for instance in instances if instance.assured]


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['offers'] = BuisnessOffersSerializer(
            instance.buisness_offers_set.all(), many=True
        ).data  
        
        sitemap_link = instance.sitemap_link.first()  # Fetch first Sitemap_Links if multiple
        if sitemap_link:
            representation['redirect_link'] = SiteSaplinksSerializerMini(sitemap_link).data
        else:
            representation['redirect_link'] = None  # Ensure proper handling

        return representation








class BuisnessesSerializerShort(serializers.ModelSerializer):
    image       = serializers.ImageField()        
    city        = serializers.StringRelatedField()
    locality    = serializers.StringRelatedField()
    plan = PlansSerializer( read_only=True)


    class Meta:
        model   = Buisnesses
        fields  = [  
                    'id','name','description',
                    'building_name','locality','city',
                    'state','pincode','opens_at','closes_at','since',
                    'instagram_link','facebook_link','web_link','x_link',
                    'youtube_link','whatsapp_number','incharge_number',
                    'image','email','manager_name','plan','no_of_views','score'
                ]
    
    












# Serializer for adding and displaying groups
class LikedBuisnessGroupSerializer(serializers.ModelSerializer):

    business_id = serializers.PrimaryKeyRelatedField(queryset=Buisnesses.objects.all(), source='business', write_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)

    class Meta:
        model = Liked_Buisnesses_Group
        fields = ['id', 'business_id', 'business_name','name']




class LikedBusinessSerializer(serializers.ModelSerializer):
    business_id = serializers.PrimaryKeyRelatedField(queryset=Buisnesses.objects.all(), source='buisness', write_only=True)
    business_name = serializers.CharField(source='buisness.name', read_only=True)
    locality = serializers.CharField(source='buisness.locality', read_only=True)
    city = serializers.CharField(source='buisness.city', read_only=True)
    image = serializers.ImageField(source='buisness.image', read_only=True)
    redirect_link = SiteSaplinksSerializerMini(source='sitemap_link', read_only=True)

    
    class Meta:
        model = Liked_Buisnesses
        fields = ['id', 'business_id', 'business_name' , 'locality' ,'city' ,'image' , 'redirect_link']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        sitemap_link = instance.buisness.sitemap_link.first()  # Fetch first Sitemap_Links if multiple
        if sitemap_link:
            representation['redirect_link'] = SiteSaplinksSerializerMini(sitemap_link).data
        else:
            representation['redirect_link'] = None  # Ensure proper handling

        return representation
        
        

class GroupWithbuisnessesSerializer(serializers.ModelSerializer):
    liked_buisnesses = serializers.SerializerMethodField()  # 
    class Meta:
        model = Liked_Buisnesses_Group
        fields = ['id', 'name', 'liked_buisnesses']

    def get_liked_buisnesses(self, obj):
        # Fetch the related Liked_Buisnesses instances for the current group
        liked_buisnesses = obj.liked_buisnesses.all()
        # Serialize the related instances using the LikedBusinessSerializer
        return LikedBusinessSerializer(liked_buisnesses, many=True).data













class EnquiriesSerializer(serializers.ModelSerializer):
    buisness = serializers.PrimaryKeyRelatedField(
    queryset=Buisnesses.objects.all(),
    )
    user = serializers.PrimaryKeyRelatedField(
    queryset=Extended_User.objects.all(),
    )
    
    class Meta:
        model = Enquiries
        fields = ['id', 'name', 'mobile_number', 'message', 'buisness', 'date', 'time','is_read' , 'user']












class ProductPicsSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Product_pics
        fields  = ['id','image']

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
            child=serializers.ImageField(), write_only=True
        )  
  
    sub_cat = serializers.PrimaryKeyRelatedField(
        queryset=Product_Sub_category.objects.all(),
        write_only=True
        )

    cat_name = serializers.CharField(source='sub_cat.cat_name', read_only=True)  # 👈 Add this

    product_images = ProductPicsSerializer(source='product_pics_set', many=True, read_only=True)


    class Meta:
        model = Products
        fields = ['id','name', 'price', 'sub_cat','cat_name', 'description',
                  'buisness', 'images','searched','product_images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Products.objects.create(**validated_data)
        
        for image in images_data:
            Product_pics.objects.create(product=product, image=image)
        
        return product
    
    
    
    
    

class ProductSerializerMini(serializers.ModelSerializer):
    images = serializers.ListField(
            child=serializers.ImageField(), write_only=True
        )  
  
    product_images = ProductPicsSerializer(source='product_pics_set', many=True, read_only=True)


    class Meta:
        model = Products
        fields = ['id','name', 'price','images','searched','product_images']






class ServicePicsSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Product_pics
        fields  = ['id','image']

class ServiceSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
            child=serializers.ImageField(), write_only=True
        )  
    cat = serializers.PrimaryKeyRelatedField(queryset=Service_Cats.objects.all(),write_only=True)
    
    cat_name = serializers.CharField(source='cat.cat_name', read_only=True)  
    
    service_images = ServicePicsSerializer(source='service_pics_set', many=True, read_only=True)


    class Meta:
        model = Products
        fields = ['id','name', 'price', 'cat_name','cat', 'description',
                  'buisness', 'images','searched','service_images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        service = Services.objects.create(**validated_data)
        
        for image in images_data:
            Service_pics.objects.create(service=service, image=image)
        
        return service




class ServiceCatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service_Cats
        fields = '__all__'  # Includes all fields in the model



class DescriptiveCatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descriptive_cats
        fields =[ 'cat_name' , 'id']
        
        
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields =[ 'city_name' , 'id']
              
class LocalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Locality
        fields =['locality_name' , 'id']

























from rest_framework import serializers

class HomeTitlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Home_Titles
        fields = ['id', 'name', 'title']


class HomePopularGeneralCatsSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField()  # To show the actual category name
    title = serializers.StringRelatedField()

    class Meta:
        model = Home_Popular_General_Cats
        fields = ['image', 'name', 'title']


class HomePopularDesCatsSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField()
    title = serializers.StringRelatedField()

    class Meta:
        model = Home_Popular_Des_Cats
        fields = ['name', 'title']


class HomePopularProductCatsSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField()
    title = serializers.StringRelatedField()

    class Meta:
        model = Home_Popular_Product_Cats
        fields = ['image', 'name', 'title']


class HomePopularCitiesSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField()
    title = serializers.StringRelatedField()

    class Meta:
        model = Home_Popular_Cities
        fields = ['image', 'name', 'title']

class HomeAdsSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField()
    banner = serializers.ImageField()

    class Meta:
        model = Home_Ads
        fields = ['banner', 'name']

class HomeMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Home_Meta_data
        fields = ['meta_title','meta_description','meta_keywords',
                  'meta_author','page_title','meta_og_image',
                  'meta_og_title','meta_og_description','meta_og_url',
                  'meta_og_site_name','meta_og_type','meta_og_image_width',
                  'meta_og_image_height','meta_og_image_alt'] 
        











class Site_Map_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Sitemap_Links
        fields = '__all__'