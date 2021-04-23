from rest_framework import serializers

from qlns.apps.attendance.models import WorkDay


class WorkdaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkDay
        fields = ('day', 'morning_from', 'morning_to', 'afternoon_from', 'afternoon_to',)
