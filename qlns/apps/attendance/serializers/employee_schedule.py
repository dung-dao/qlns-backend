from rest_framework import serializers

from qlns.apps.attendance.models import EmployeeSchedule, Schedule
from qlns.apps.attendance.serializers import ScheduleSerializer
from qlns.apps.core.models import Employee


class EmployeeScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSchedule
        fields = ('schedule', 'owner',)

    schedule = ScheduleSerializer(read_only=True)
    owner = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())

    def create(self, validated_data):
        modified_validated_data = validated_data
        request = self.context['request']
        schedule_name = request.data.get('schedule')
        schedule = Schedule.objects.filter(name=schedule_name).first()
        modified_validated_data['schedule'] = schedule

        return super(EmployeeScheduleSerializer, self).create(modified_validated_data)

    def update(self, instance, validated_data):
        modified_validated_data = validated_data
        request = self.context['request']
        schedule_name = request.data.get('schedule')
        schedule = Schedule.objects.filter(name=schedule_name).first()
        modified_validated_data['schedule'] = schedule
        return super(EmployeeScheduleSerializer, self).update(instance, modified_validated_data)
