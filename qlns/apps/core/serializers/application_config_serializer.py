from rest_framework import serializers

from qlns.apps.core.models import ApplicationConfig


class ApplicationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ApplicationConfig
