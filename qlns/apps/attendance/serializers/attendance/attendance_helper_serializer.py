from rest_framework import serializers

from qlns.apps.job.serializers import LocationSerializer


class AttendanceHelperSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        raise Exception('unreachable code')

    def create(self, validated_data):
        raise Exception('unreachable code')

    next_step = serializers.CharField(read_only=True)
    first_clock_in = serializers.DateTimeField(read_only=True)
    last_clock_out = serializers.DateTimeField(read_only=True)
    last_action = serializers.CharField(read_only=True)
    last_action_at = serializers.DateTimeField(read_only=True)
    location = LocationSerializer(read_only=True)
