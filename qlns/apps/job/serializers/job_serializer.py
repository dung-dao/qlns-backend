from rest_framework import serializers

from qlns.apps.core import models as core_models
from qlns.apps.job import models as job_models


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = (
            'is_terminated',
            'termination_reason',
            'termination_date',
            'termination_note')
        model = job_models.Job

    department = serializers.SlugRelatedField(
        'name',
        queryset=core_models.Department.objects.all(),
        allow_null=True)
    job_title = serializers.SlugRelatedField(
        'name',
        queryset=job_models.JobTitle.objects.all(),
        allow_null=True)
    location = serializers.SlugRelatedField(
        'name',
        queryset=job_models.Location.objects.all(),
        allow_null=True)
    employment_status = serializers.SlugRelatedField(
        'name',
        queryset=job_models.EmploymentStatus.objects.all(),
        allow_null=False)
