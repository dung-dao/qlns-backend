from rest_framework import serializers
from qlns.apps.core import models as core_models


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.Language
        fields = '__all__'
