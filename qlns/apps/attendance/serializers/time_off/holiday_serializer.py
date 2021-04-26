from rest_framework import serializers

from qlns.apps.attendance.models import Holiday


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
