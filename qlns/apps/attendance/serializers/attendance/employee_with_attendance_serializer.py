from rest_framework import serializers

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
    schedule_hours = serializers.FloatField(read_only=True, source='get_schedule_hours')

    class Meta:
        model = Attendance
        fields = ('id', 'owner', 'date',
                  'actual_work_hours',
                  'actual_hours_modified',
                  'actual_hours_modification_note',

                  'ot_work_hours',
                  'ot_hours_modified',
                  'ot_hours_modification_note',

                  'reviewed_by', 'confirmed_by', 'status', 'schedule_hours')
        list_serializer_class = FilteredAttendanceListSerializer


class EmployeeWithAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name', 'avatar', 'attendance')

    attendance = FilteredAttendanceSerializer(many=True)
