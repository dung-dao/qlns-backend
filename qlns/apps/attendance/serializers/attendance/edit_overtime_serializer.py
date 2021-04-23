from rest_framework import serializers


class EditOvertimeSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    ot_work_hours = serializers.FloatField(required=True)
    ot_hours_modification_note = serializers.CharField(required=True)
