from rest_framework import serializers

from qlns.apps.attendance.models import Tracking


class TrackingSerializer(serializers.ModelSerializer):
    location = serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        model = Tracking
        exclude = ('attendance',)
