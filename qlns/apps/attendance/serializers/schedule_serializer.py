from rest_framework import serializers

from qlns.apps.attendance.models import Schedule, WorkDay
from qlns.apps.attendance.serializers.workday_serializer import WorkdaySerializer


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'name', 'workdays',)

    workdays = WorkdaySerializer(read_only=False, many=True)

    def create(self, validated_data):
        workdays = validated_data.pop('workdays')

        schedule = Schedule(name=validated_data['name'])
        schedule.save()

        for wd in workdays:
            workday = WorkDay(**wd)
            workday.schedule = schedule
            workday.save()

        return schedule

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        instance.workdays.all().delete()

        workdays = validated_data.pop('workdays')
        for wd in workdays:
            workday = WorkDay(**wd)
            workday.schedule = instance
            workday.save()
        return instance
