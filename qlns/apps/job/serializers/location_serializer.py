from rest_framework import serializers

from qlns.apps.job import models as job_models


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = job_models.Location
        fields = '__all__'

    def validate(self, attrs):
        enable_geofencing = attrs.get('enable_geofencing', False)

        lat_is_none = attrs.get('lat', None) is None
        lng_is_none = attrs.get('lng', None) is None
        radius_is_none = attrs.get('radius', None) is None
        accurate_address_is_none = attrs.get('accurate_address', None) is None

        if not enable_geofencing:
            if not lat_is_none or \
                    not lng_is_none or \
                    not radius_is_none or \
                    not accurate_address_is_none:
                raise serializers.ValidationError("Redundant geo info")
        else:
            if lat_is_none or \
                    lng_is_none or \
                    radius_is_none or \
                    accurate_address_is_none:
                raise serializers.ValidationError("Geo Info required")
        return attrs
