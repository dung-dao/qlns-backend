from rest_framework import serializers

from qlns.apps.attendance.models import TimeOffType


class TimeOffTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeOffType
        fields = '__all__'
