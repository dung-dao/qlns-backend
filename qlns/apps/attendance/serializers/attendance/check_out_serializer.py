from rest_framework import serializers


class CheckOutDataSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    check_out_lat = serializers.FloatField(required=False)
    check_out_lng = serializers.FloatField(required=False)
    face_image = serializers.ImageField(required=False)
