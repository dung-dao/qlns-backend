from rest_framework import serializers

from qlns.apps.job.models import EmploymentStatus


class EmploymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentStatus
        fields = '__all__'
