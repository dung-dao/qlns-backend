from django.db.models import Q
from rest_framework import serializers

from qlns.apps.attendance import models as attendance_models
from qlns.apps.attendance.models import Attendance
from qlns.apps.core.models import Employee


class FilteredAttendanceListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        raise Exception("Unreachable code")

    def to_representation(self, data):
        data = data.filter(
            date__gte=self.context.get('start_date'),
            date__lte=self.context.get('end_date')
        )
        period_id = self.context.get("period_id")
        if period_id is not None:
            data = data.filter(period=period_id)
        return super().to_representation(data)


class FilteredAttendanceSerializer(serializers.ModelSerializer):
    # schedule_hours = serializers.FloatField(read_only=True, source='get_schedule_hours')

    class Meta:
        model = Attendance
        fields = ('id', 'owner', 'date',
                  'actual_work_hours',
                  'actual_hours_modified',
                  'actual_hours_modification_note',

                  'ot_work_hours',
                  'ot_hours_modified',
                  'ot_hours_modification_note',

                  'reviewed_by', 'confirmed_by', 'status',)
        list_serializer_class = FilteredAttendanceListSerializer


class EmployeeWithAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name', 'avatar', 'attendance')

    attendance = FilteredAttendanceSerializer(many=True)

    def to_representation(self, instance):
        representation = super(EmployeeWithAttendanceSerializer, self).to_representation(instance)

        period_id = self.context.get("period_id", None)
        if period_id is not None:
            period = attendance_models.Period.objects.filter(pk=int(period_id)).first()
            if period is not None:
                period_start_date = period.start_date
                period_end_date = period.end_date
                schedule = instance.get_current_schedule()

                if schedule is not None:
                    schedule_work_hours = schedule.get_work_hours(period_start_date, period_end_date)
                    holidays = attendance_models.Holiday.objects \
                        .filter(Q(start_date__gte=period_start_date) &
                                Q(start_date__lte=period_end_date) &
                                Q(schedule=schedule))
                    holiday_hours = sum(
                        list(map(lambda hld: hld.trim_work_hours(period_start_date, period_end_date), holidays)))
                    representation["schedule_hours"] = schedule_work_hours - holiday_hours / 24 * 8
                else:
                    representation["schedule_hours"] = 0
        return representation
