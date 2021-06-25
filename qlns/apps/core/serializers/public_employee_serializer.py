from rest_framework import serializers

from qlns.apps.core.models import Employee


class PublicEmployeeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, source='get_username')

    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name', 'full_name', 'email', 'avatar', 'username',)
