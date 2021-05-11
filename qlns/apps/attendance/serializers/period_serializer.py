from rest_framework import serializers

from qlns.apps.attendance.models import Period


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Period
