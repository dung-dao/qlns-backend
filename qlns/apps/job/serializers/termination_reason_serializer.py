from rest_framework import serializers

from qlns.apps.job import models as job_models


class TerminationReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = job_models.TerminationReason
        exclude = ()
