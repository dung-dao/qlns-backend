from rest_framework import serializers


class CheckInDataSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    check_in_lat = serializers.FloatField(required=False)
    check_in_lng = serializers.FloatField(required=False)
    face_image = serializers.ImageField(required=False)
