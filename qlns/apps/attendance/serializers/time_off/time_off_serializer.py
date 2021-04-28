from rest_framework import serializers

from qlns.apps.attendance.models import TimeOff, TimeOffType


class TimeOffSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewed_by = serializers.PrimaryKeyRelatedField(read_only=True)
    time_off_type = serializers.SlugRelatedField('name', read_only=False, queryset=TimeOffType.objects.all())
    status = serializers.CharField(read_only=True)
    schedule = serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        model = TimeOff
        fields = ('id', 'owner', 'reviewed_by',
                  'time_off_type', 'start_date', 'end_date',
                  'status', 'note', 'schedule', 'work_hours')
        read_only_fields = ('work_hours',)

    def create(self, validated_data):
        params = validated_data
        params['owner'] = self.context.get('owner')
        params['status'] = TimeOff.TimeOffStatus.Pending
        params['schedule'] = self.context.get('owner').get_current_schedule()
        time_off = TimeOff(**params)
        time_off.calculate_work_hours()
        time_off.save()
        return time_off

    def update(self, instance, validated_data):
        raise NotImplemented
