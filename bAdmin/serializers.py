# serializers.py
from rest_framework import serializers
from usershome.models import *







class DescriptiveCatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descriptive_cats
        fields = ['id', 'cat_name', 'general_cat', 'maped']







class GeneralCatsSerializer(serializers.ModelSerializer):
    dcats_count = serializers.IntegerField(read_only=True)
    # dcats       = serializers.SerializerMethodField()
    class Meta:
        model = General_cats
        fields = ['id', 'cat_name', 'dcats_count' ]

    # def get_dcats(self, obj):
    #     return DescriptiveCatsSerializer(Descriptive_cats.objects.filter(general_cat = obj) , many=True).data
        
        
        
        
        
        
        

class ProductGeneralCatsSerializer(serializers.ModelSerializer):
    dcats_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product_General_category
        fields = ['id', 'cat_name','dcats_count']


class ProductSubCatsSerializer(serializers.ModelSerializer):
    gcat = serializers.SerializerMethodField()
    class Meta:
        model = Product_Sub_category
        fields = ['id', 'cat_name','gcat']
    
    def get_gcat(self , obj):
        return obj.general_cat.cat_name
    
    
class BuisnessesAdminlistSerializer(serializers.ModelSerializer):
    plan = serializers.SerializerMethodField()
    image = serializers.ImageField()
    city = serializers.SerializerMethodField()
    locality = serializers.SerializerMethodField()
    class Meta:
        model = Buisnesses
        fields = ['id', 'name', 'building_name','locality', 'city', 'state', 'verified', 'created_on', 'assured', 'plan' , 'rating','image' , 'buisness_type']
    
    def get_plan(self, obj):
        return obj.plan.plan_name if obj.plan else None
    