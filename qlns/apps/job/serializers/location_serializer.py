from rest_framework import serializers
from qlns.apps.job import models


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = '__all__'
