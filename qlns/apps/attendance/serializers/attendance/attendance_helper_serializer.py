from rest_framework import serializers


class AttendanceHelperSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    next_step = serializers.CharField()
    first_clock_in = serializers.DateTimeField()
    last_clock_out = serializers.DateTimeField()
    last_action = serializers.CharField()
    last_action_at = serializers.DateTimeField()
