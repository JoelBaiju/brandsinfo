# serializers.py
from rest_framework import serializers
from usershome.models import General_cats ,Descriptive_cats

class GeneralCatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = General_cats
        fields = ['id', 'cat_name']

class DescriptiveCatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descriptive_cats
        fields = ['id', 'cat_name', 'general_cat', 'maped']
