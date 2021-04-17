from rest_framework import serializers
from qlns.apps.core import models as core_models


class EducationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.EducationLevel
        fields = '__all__'
