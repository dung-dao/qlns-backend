from rest_framework import serializers

from qlns.apps.attendance.models import EmployeeSchedule, Schedule
from qlns.apps.core.models import Employee


class EmployeeScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSchedule
        fields = ('schedule', 'owner',)

    schedule = serializers.SlugRelatedField('name', queryset=Schedule.objects.all())
    owner = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
