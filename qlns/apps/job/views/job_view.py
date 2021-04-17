from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from qlns.apps.job.models import Job
from qlns.apps.job.serializers import JobSerializer


class JobView(viewsets.GenericViewSet,
              mixins.ListModelMixin,
              mixins.RetrieveModelMixin,
              mixins.CreateModelMixin,
              mixins.DestroyModelMixin):
    serializer_class = JobSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Job.objects.filter(owner=self.kwargs['employee_pk']).order_by('-timestamp')

    def create(self, request, *args, **kwargs):
        employee_id = self.kwargs['employee_pk']
        if 'owner' not in request.data or employee_id != str(request.data['owner']):
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid owner")
        return super(JobView, self).create(request, *args, **kwargs)
