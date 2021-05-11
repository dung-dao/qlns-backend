from rest_framework import serializers

from qlns.apps.attendance.models import Tracking


class TrackingSerializer(serializers.ModelSerializer):
    location = serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        model = Tracking
        fields = ('is_overtime',
                  'check_in_time', 'check_in_lat', 'check_in_lng', 'check_in_outside',
                  'check_out_time', 'check_out_lat', 'check_out_lng', 'check_out_outside',
                  'check_in_note', 'check_out_note', 'location',
                  'actual_work_hours', 'ot_work_hours')
