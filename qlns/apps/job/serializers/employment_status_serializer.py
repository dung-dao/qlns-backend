from rest_framework import serializers

from qlns.apps.job import models as job_models


class EmploymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = job_models.EmploymentStatus
        fields = '__all__'
