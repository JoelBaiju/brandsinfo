from rest_framework import serializers
from .models import * 



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extended_User
        fields=['mobile_number','first_name']
        



class Popular_general_cats_serializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='general_cat', read_only=True)
    id = serializers.PrimaryKeyRelatedField(source='general_cat', read_only=True)  # Returns the ID
    
    class Meta:
        model = Popular_General_Cats
        fields = ['name', 'id']
        


class BuisnessPicsSerializer(serializers.ModelSerializer):
    buisness    = serializers.PrimaryKeyRelatedField(
                    queryset = Buisnesses.objects.all()
                )
    image       = serializers.ImageField()
    
    class Meta:
        model  = Buisness_pics
        fields  = [
                    'image' ,
                    'buisness' ,
                  ]



class BuisnessesSerializer(serializers.ModelSerializer):
    image       = serializers.ImageField(required=False)
    city        = serializers.StringRelatedField()
    locality    = serializers.PrimaryKeyRelatedField(queryset=Locality.objects.all())
    user        = serializers.PrimaryKeyRelatedField(
                    queryset=Extended_User.objects.all()
                    )
    image_gallery = BuisnessPicsSerializer(many=True, read_only=True)

    
    class Meta:
        model = Buisnesses
        fields=['id',
                'name',
                'description',
                'buisness_type',
                'manager_name',
                'building_name',
                'locality',
                'city',
                'state',
                'pincode',
                'latittude',
                'longitude',
                'opens_at',
                'closes_at',
                'since',
                'no_of_views',
                'instagram_link',
                'facebook_link',
                'web_link',
                'x_link',
                'youtube_link',
                'whatsapp_number',
                'incharge_number',
                'user',
                'score',
                'image',
                'sa_rate',  
                'no_of_enquiries',
                'email'
                ]
        
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = BuisnessPicsSerializer(
            instance.buisness_pics_set.all(), many=True
        ).data
        return representation
    
    def create(self, validated_data):
        user=validated_data.pop('owner', None)  
        # obj=Buisnesses.objects.create(**validated_data)
        # obj.user=user
        # return 
        return Buisnesses.objects.create(**validated_data)
    
    
    

class BuisnessesSerializerFull(serializers.ModelSerializer):
    image       = serializers.ImageField(required=False)
    city        = serializers.StringRelatedField()
    locality    = serializers.StringRelatedField()
    user        = serializers.PrimaryKeyRelatedField(
                    queryset=Extended_User.objects.all()
                    )

    
    class Meta:
        model = Buisnesses
        fields=['id',
                'name',
                'description',
                'buisness_type',
                'manager_name',
                'building_name',
                'locality',
                'city',
                'state',
                'pincode',
                'latittude',
                'longitude',
                'opens_at',
                'closes_at',
                'since',
                'no_of_views',
                'instagram_link',
                'facebook_link',
                'web_link',
                'x_link',
                'youtube_link',
                'whatsapp_number',
                'incharge_number',
                'user',
                'score',
                'image',
                'sa_rate',  
                'no_of_enquiries',
                'email'
                ]
    
    



class BuisnessesSerializerCustomers(serializers.ModelSerializer):
    image       = serializers.ImageField()
    city        = serializers.StringRelatedField()
    locality    = serializers.StringRelatedField()
    user        = serializers.PrimaryKeyRelatedField(
                    queryset=Extended_User.objects.all()
                    )
    image_gallery = BuisnessPicsSerializer(many=True, read_only=True)
    
    class Meta:
        model   = Buisnesses
        fields  = [  'id',
                    'name',
                    'description',
                    'buisness_type',
                    'manager_name',
                    'building_name',
                    'locality',
                    'city',
                    'state',
                    'pincode',
                    'latittude',
                    'longitude',
                    'opens_at',
                    'closes_at',
                    'since',
                    'no_of_views',
                    'instagram_link',
                    'facebook_link',
                    'web_link',
                    'x_link',
                    'youtube_link',
                    'whatsapp_number',
                    'incharge_number',
                    'user',
                    'image',
                    'image_gallery'
                 ]
    


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image_gallery'] = BuisnessPicsSerializer(
            instance.buisness_pics_set.all(), many=True
        ).data
        return representation


class BuisnessesSerializerMini(serializers.ModelSerializer):
    image       = serializers.ImageField()        
    city        = serializers.StringRelatedField()
    locality    = serializers.StringRelatedField()
    user        = serializers.PrimaryKeyRelatedField(
                    queryset=Extended_User.objects.all()
                )
    
    class Meta:
        model   = Buisnesses
        fields  = [  
                    'id',
                    'name',
                    'buisness_type',
                    'locality',
                    'city',
                    'state',
                    'no_of_views',
                    'user',
                    'score',
                    'image'
                 ]
    










class ProductPicsSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Product_pics
        fields  = ['image']

class ProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
            child=serializers.ImageField(), write_only=True
        )  
  
    sub_cat = serializers.PrimaryKeyRelatedField(
    queryset=Product_Sub_category.objects.all(),
)

    
    product_images = ProductPicsSerializer(source='product_pics_set', many=True, read_only=True)


    class Meta:
        model = Products
        fields = ['id','name', 'price', 'sub_cat', 'description', 'buisness', 'images','searched','product_images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Products.objects.create(**validated_data)
        
        for image in images_data:
            Product_pics.objects.create(product=product, image=image)
        
        return product



class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
            child=serializers.ImageField(), write_only=True
        )  
  
    sub_cat = serializers.StringRelatedField()
    product_images = ProductPicsSerializer(source='product_pics_set', many=True, read_only=True)


    class Meta:
        model = Products
        fields = ['id','name', 'price', 'sub_cat', 'description', 'buisness', 'images','searched','product_images']







class CreateServiceSerializer(serializers.ModelSerializer):

    cat = serializers.PrimaryKeyRelatedField(
    queryset=Service_Cats.objects.all(),
)    
    class Meta:
        model = Services
        fields = '__all__'  # Includes all fields in the model



class ServiceSerializer(serializers.ModelSerializer):

    cat = serializers.StringRelatedField()

    class Meta:
        model = Services
        fields = '__all__'  # Includes all fields in the model



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
