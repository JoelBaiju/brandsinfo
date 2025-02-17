from rest_framework import serializers
from .models import * 



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extended_User
        fields=['mobile_number','first_name']
        

class BuisnessesSerializer(serializers.ModelSerializer):
    # profile_pic = serializers.ImageField()
    city = serializers.PrimaryKeyRelatedField(
            queryset=City.objects.all()
        ) 
    locality = serializers.PrimaryKeyRelatedField(
            queryset=Locality.objects.all()
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
                'whatsapp_number',
                'incharge_number',
                'user'
                ]
    
    def create(self, validated_data):
        user=validated_data.pop('owner', None)  
        # obj=Buisnesses.objects.create(**validated_data)
        # obj.user=user
        # return 
        return Buisnesses.objects.create(**validated_data)
    
    
class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['name', 'price', 'image', 'cat', 'description']



# class ProductRetrieveSerializer(serializers.ModelSerializer):
#     images = serializers.SerializerMethodField()
#     categories = serializers.Serializer




# class ProductAddSerializer(serializers.ModelSerializer):
#     images = serializers.ListField(
#         child=serializers.ImageField(), write_only=True, required=False
#     )
#     categories = serializers.ListField(
#         child=serializers.IntegerField(), write_only=True, required=False
#     )

#     class Meta:
#         model = Products
#         fields = ['name', 'price', 'image', 'cat', 'description', 'images', 'categories']

#     def create(self, validated_data):
#         images_data = validated_data.pop('images', [])
#         categories_data = validated_data.pop('categories', [])

#         product = Products.objects.create(**validated_data)

#         # Save additional product images
#         for image in images_data:
#             Product_pics.objects.create(product=product, pic=image)

#         # Save product categories
#         for cat_id in categories_data:
#             category = Product_category.objects.create(product=product, cat_name=cat_id)

#         return product


class ProductPicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_pics
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
            child=serializers.ImageField(), write_only=True
        )  
    sub_cat = serializers.PrimaryKeyRelatedField(
            queryset=Product_Sub_category.objects.all()
        ) 

    class Meta:
        model = Products
        fields = ['name', 'price', 'sub_cat', 'description', 'buisness', 'images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Products.objects.create(**validated_data)
        
        for image in images_data:
            Product_pics.objects.create(product=product, image=image)
        
        return product




class ServiceSerializer(serializers.ModelSerializer):
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
