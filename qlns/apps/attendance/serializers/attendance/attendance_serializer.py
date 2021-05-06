from rest_framework import serializers

from qlns.apps.attendance.models import Attendance
from qlns.apps.attendance.serializers.attendance.TrackingSerializer import TrackingSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ('id', 'owner', 'date',
                  'actual_work_hours',
                  'actual_hours_modified',
                  'actual_hours_modification_note',

                  'ot_work_hours',
                  'ot_hours_modified',
                  'ot_hours_modification_note',
                  'is_confirmed',
                  'reviewed_by', 'confirmed_by', 'status', 'tracking_data',)

    tracking_data = TrackingSerializer(read_only=True, many=True)
