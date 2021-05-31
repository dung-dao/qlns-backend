from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from qlns.apps.job import models as job_models
from qlns.apps.job import serializers as job_serializer


class JobTitleView(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = job_serializer.JobTitleSerializer
    queryset = job_models.JobTitle.objects.all()
