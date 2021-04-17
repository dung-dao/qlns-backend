from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from qlns.apps.job.models import JobEvent
from qlns.apps.job.serializers import JobEventSerializer


class JobEventView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = JobEventSerializer
    queryset = JobEvent.objects.all()
