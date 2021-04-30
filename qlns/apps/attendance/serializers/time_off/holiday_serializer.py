from django.db.transaction import atomic
from rest_framework import serializers

from qlns.apps.attendance.models import Holiday


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'

    @atomic
    def update(self, instance, validated_data):
        holiday = super(HolidaySerializer, self).update(instance, validated_data)
        holiday.calculate_work_hours()
        holiday.save()
        return holiday

    @atomic
    def create(self, validated_data):
        holiday = super(HolidaySerializer, self).create(validated_data)
        holiday.calculate_work_hours()
        holiday.save()
        return holiday
