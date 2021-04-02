from rest_framework import serializers
from qlns.apps.core import models as core_models


class EmergencyContactSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=core_models.Employee.objects.all())

    class Meta:
        model = core_models.EmergencyContact
        fields = '__all__'
