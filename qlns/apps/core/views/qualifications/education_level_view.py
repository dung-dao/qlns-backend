from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from qlns.apps.core import models as core_models
from qlns.apps.core.serializers import qualifications as qualification_serializers


class EducationLevelView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = qualification_serializers.EducationLevelSerializer
    queryset = core_models.EducationLevel.objects.all()
