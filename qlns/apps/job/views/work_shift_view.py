from rest_framework import viewsets

from qlns.apps.job import models as job_models
from qlns.apps.job import serializers as job_serializers


class WorkShiftView(viewsets.ModelViewSet):
    serializer_class = job_serializers.WorkShiftSerializer
    queryset = job_models.WorkShift.objects.all()
