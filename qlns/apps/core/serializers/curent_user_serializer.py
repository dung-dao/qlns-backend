from .employee_serializer import EmployeeSerializer
from qlns.apps.authentication import serializers as auth_serializers
from rest_framework import serializers


class CurrentUserSerializer(EmployeeSerializer):
    permissions = serializers.ListField(
        child=serializers.CharField(max_length=255),
        source='get_permissions',
        read_only=True,
    )

    class Meta:
        fields = EmployeeSerializer.Meta.fields
        model = EmployeeSerializer.Meta.model
