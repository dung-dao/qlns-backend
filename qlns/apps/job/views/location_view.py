from rest_framework import viewsets

from qlns.apps.job import models as job_models
from qlns.apps.job import serializers as job_serializers


class LocationView(viewsets.ModelViewSet):
    serializer_class = job_serializers.LocationSerializer
    queryset = job_models.Location.objects.all()
