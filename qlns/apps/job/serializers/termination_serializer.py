from rest_framework import serializers


class TerminationSerializer(serializers.Serializer):
    termination_reason = serializers.CharField(required=True)
    termination_date = serializers.DateTimeField(required=True)
    termination_note = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        raise Exception('unreachable code')

    def create(self, validated_data):
        raise Exception('unreachable code')
