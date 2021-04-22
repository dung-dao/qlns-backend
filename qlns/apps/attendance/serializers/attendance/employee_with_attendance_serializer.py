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
        return super().to_representation(data)


class FilteredAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ('id', 'owner', 'date', 'actual_work_hours', 'ot_work_hours',
                  'reviewed_by', 'confirmed_by', 'status',)
        list_serializer_class = FilteredAttendanceListSerializer
    # tracking_data = TrackingSerializer(read_only=True, many=True)


class EmployeeWithAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name', 'avatar', 'attendance', 'employment_status')

    attendance = FilteredAttendanceSerializer(many=True)
    employment_status = serializers.CharField(source='get_employment_status', read_only=True)
