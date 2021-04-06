from rest_framework import viewsets

from qlns.apps.job.models import JobTitle
from qlns.apps.job.serializers.job_title_serializer import JobTitleSerializer


class JobTitleView(viewsets.ModelViewSet):
    serializer_class = JobTitleSerializer
    queryset = JobTitle.objects.all()
