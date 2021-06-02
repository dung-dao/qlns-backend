from datetime import timedelta

from django.db.transaction import atomic
from django_q.models import Schedule as Q_Schedule
from rest_framework import serializers

from qlns.apps.attendance.models import Schedule, WorkDay
from qlns.apps.attendance.serializers.workday_serializer import WorkdaySerializer
from qlns.apps.core.models import ApplicationConfig
from qlns.utils.datetime_utils import CRON_WEEKDAYS, PY_WEEKDAYS, to_cron_weekday


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

        # Delete all schedule
        q_schedule_name = 'CheckOutSchedule_' + instance.name
        config = ApplicationConfig.objects.first()
        early_check_in_minutes = config.early_check_in_minutes
        Q_Schedule.objects.filter(name=q_schedule_name).delete()

        # Shift-end check out
        for wd in instance.workdays.all():
            cron_weekday = CRON_WEEKDAYS[wd.day]

            if wd.morning_from is not None:
                morning_from = wd.morning_from
                while morning_from.weekday() != PY_WEEKDAYS[wd.day]:
                    morning_from += timedelta(days=1)
                early_morning = morning_from - timedelta(minutes=early_check_in_minutes)

                Q_Schedule.objects.create(
                    name=q_schedule_name,
                    func='qlns.apps.attendance.tasks.auto_checkout',
                    schedule_type=Q_Schedule.CRON,
                    cron=f'{early_morning.minute} {early_morning.hour} * * {to_cron_weekday(early_morning.weekday())}'
                )

                morning_to = wd.morning_to
                while morning_to.weekday() != PY_WEEKDAYS[wd.day]:
                    morning_to += timedelta(days=1)

                Q_Schedule.objects.create(
                    name=q_schedule_name,
                    func='qlns.apps.attendance.tasks.auto_checkout',
                    schedule_type=Q_Schedule.CRON,
                    cron=f'{morning_to.minute} {morning_to.hour} * * {to_cron_weekday(morning_to.weekday())}'
                )

            if wd.afternoon_from is not None:
                afternoon_from = wd.afternoon_from
                while afternoon_from.weekday() != PY_WEEKDAYS[wd.day]:
                    afternoon_from += timedelta(days=1)
                early_afternoon = afternoon_from - timedelta(minutes=early_check_in_minutes)
                Q_Schedule.objects.create(
                    name=q_schedule_name,
                    func='qlns.apps.attendance.tasks.auto_checkout',
                    schedule_type=Q_Schedule.CRON,
                    cron=f'{early_afternoon.minute} {early_afternoon.hour} * * {to_cron_weekday(early_afternoon.weekday())}'
                )

                afternoon_to = wd.afternoon_to
                while afternoon_to.weekday() != PY_WEEKDAYS[wd.day]:
                    afternoon_to += timedelta(days=1)

                Q_Schedule.objects.create(
                    name=q_schedule_name,
                    func='qlns.apps.attendance.tasks.auto_checkout',
                    schedule_type=Q_Schedule.CRON,
                    cron=f'{afternoon_to.minute} {afternoon_to.hour} * * {to_cron_weekday(afternoon_to.weekday())}'
                )

        return instance
