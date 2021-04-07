from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from qlns.apps.job.models import EmploymentStatus
from qlns.apps.job.serializers import EmploymentStatusSerializer


class EmploymentStatusView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmploymentStatusSerializer
    queryset = EmploymentStatus.objects.all()
