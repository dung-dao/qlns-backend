from rest_framework import serializers


class EditActualSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    actual_work_hours = serializers.FloatField(required=True)
    actual_hours_modification_note = serializers.CharField(required=True)
