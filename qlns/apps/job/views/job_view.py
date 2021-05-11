from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.core.models import Employee
from qlns.apps.job.models import Job
from qlns.apps.job.serializers import JobSerializer
from qlns.apps.job.serializers.termination_serializer import TerminationSerializer


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

    @action(detail=False, methods=['post'])
    def terminate_employment(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, pk=self.kwargs['employee_pk'])
        serializer = TerminationSerializer(data=self.request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        job = employee.get_current_job()
        if job is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="NO JOB")

        if job.is_terminated:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        field_dict = serializer.data
        job.pk = None
        job.event = Job.JobEvent.Terminated
        job.is_terminated = True
        job.termination_date = field_dict.get('termination_date')
        job.termination_reason = field_dict.get('termination_reason')
        job.termination_note = field_dict.get('termination_note', None)
        job.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
