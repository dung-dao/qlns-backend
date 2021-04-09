from rest_framework import serializers
from qlns.apps.core import models as core_models


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.License
        fields = '__all__'
