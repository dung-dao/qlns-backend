from rest_framework import serializers

from qlns.apps.attendance.models import Attendance
from qlns.apps.attendance.serializers.attendance.TrackingSerializer import TrackingSerializer
from qlns.apps.core.serializers.public_employee_serializer import PublicEmployeeSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    schedule_hours = serializers.FloatField(read_only=True, source='get_schedule_hours')
    owner = PublicEmployeeSerializer()

    class Meta:
        model = Attendance
        fields = ('id', 'owner', 'date',
                  'actual_work_hours',
                  'actual_hours_modified',
                  'actual_hours_modification_note',

                  'ot_work_hours',
                  'ot_hours_modified',
                  'ot_hours_modification_note',
                  'reviewed_by', 'confirmed_by', 'status', 'tracking_data', 'schedule_hours')

    tracking_data = TrackingSerializer(read_only=True, many=True)
