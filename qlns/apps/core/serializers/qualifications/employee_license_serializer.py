from rest_framework import serializers

from qlns.apps.core import models as core_models


class EmployeeLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.EmployeeLicense
        fields = '__all__'

    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    license_type = serializers.SlugRelatedField('name', read_only=False, queryset=core_models.License.objects.all())
