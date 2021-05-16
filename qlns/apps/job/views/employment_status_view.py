from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from qlns.apps.job import models as job_models
from qlns.apps.job import serializers as job_serializer


class EmploymentStatusView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = job_serializer.EmploymentStatusSerializer
    queryset = job_models.EmploymentStatus.objects.all()
