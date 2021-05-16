from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from qlns.apps.job import models as job_models
from qlns.apps.job import serializers as job_serializer


class TerminationReasonView(viewsets.ModelViewSet):
    serializer_class = job_serializer.TerminationReasonSerializer
    queryset = job_models.TerminationReason.objects.all()
    permission_classes = (IsAuthenticated,)
