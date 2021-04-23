from rest_framework import serializers

from qlns.apps.attendance.models import OvertimeType


class OvertimeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimeType
        fields = '__all__'
