# serializers.py
from rest_framework import serializers
from usershome.models import General_cats ,Descriptive_cats







class DescriptiveCatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descriptive_cats
        fields = ['id', 'cat_name', 'general_cat', 'maped']



class GeneralCatsSerializer(serializers.ModelSerializer):
    dcats_count = serializers.IntegerField(read_only=True)
    # dcats       = serializers.SerializerMethodField()
    class Meta:
        model = General_cats
        fields = ['id', 'cat_name', 'dcats_count' , 'dcats']

    # def get_dcats(self, obj):
    #     return DescriptiveCatsSerializer(Descriptive_cats.objects.filter(general_cat = obj) , many=True).data
        
        