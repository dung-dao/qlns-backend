from django.db.transaction import atomic
from rest_framework import serializers

from qlns.apps.attendance.models import Schedule, WorkDay
from qlns.apps.attendance.serializers.workday_serializer import WorkdaySerializer


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'name', 'workdays',)

    workdays = WorkdaySerializer(read_only=False, many=True)

    def validate(self, attrs):
        workdays = attrs.get('workdays')
        for wd in workdays:
            morning_from = wd.get('morning_from', None)
            morning_to = wd.get('morning_to', None)
            afternoon_from = wd.get('afternoon_from', None)
            afternoon_to = wd.get('afternoon_to', None)

            if ((morning_from is None) != (morning_to is None)) or \
                    ((afternoon_from is None) != (afternoon_to is None)):
                raise serializers.ValidationError('Invalid schedule')

            if morning_from is not None and morning_from >= morning_to:
                raise serializers.ValidationError('Invalid schedule')

            if afternoon_from is not None and afternoon_from >= afternoon_to:
                raise serializers.ValidationError('Invalid schedule')

        return attrs

    @atomic
    def create(self, validated_data):
        workdays = validated_data.pop('workdays')

        schedule = Schedule(name=validated_data['name'])
        schedule.save()

        for wd in workdays:
            workday = WorkDay(**wd)
            workday.schedule = schedule
            workday.save()

        return schedule

    @atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        instance.workdays.all().delete()

        workdays = validated_data.pop('workdays')
        for wd in workdays:
            workday = WorkDay(**wd)
            workday.schedule = instance
            workday.save()

        instance.update_duration()
        return instance
