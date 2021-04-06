from rest_framework import serializers
from qlns.apps.job import models as job_models


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = job_models.JobTitle
        fields = '__all__'
