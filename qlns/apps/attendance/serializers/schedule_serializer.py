from rest_framework import serializers

from qlns.apps.attendance.models import Schedule, WorkDay
from qlns.apps.attendance.serializers.workday_serializer import WorkdaySerializer


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'name', 'workdays', 'time_zone')

    workdays = WorkdaySerializer(read_only=False, many=True)

    def validate(self, attrs):
        workdays = attrs.get('workdays')
        for wd in workdays:
            morning_from = wd.get('morning_from', None)
            morning_to = wd.get('morning_to', None)
            afternoon_from = wd.get('afternoon_from', None)
            afternoon_to = wd.get('afternoon_to', None)

            if morning_from is None and morning_to is not None or \
                    afternoon_from is None and afternoon_to is not None or \
                    morning_from.time() >= morning_to.time() or \
                    afternoon_from.time() >= afternoon_to.time():
                raise serializers.ValidationError('Invalid schedule')
        return attrs

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
