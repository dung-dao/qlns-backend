from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django_q.models import Schedule as Q_Schedule
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.authentication.permissions import CRUDPermission, DjangoModelPermissionOrIsOwner, ActionPermission
from qlns.apps.core import models as core_models
from qlns.apps.job import models as job_models
from qlns.apps.job import serializers as job_serializer


class JobView(viewsets.GenericViewSet,
              mixins.ListModelMixin,
              mixins.RetrieveModelMixin,
              mixins.CreateModelMixin, ):
    serializer_class = job_serializer.JobSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_permissions(self):
        permission_classes = (permissions.IsAuthenticated,)
        if self.action in ['create', 'destroy', ]:
            permission_classes = (CRUDPermission,)
        if self.action in ['list', 'retrieve']:
            permission_classes = (DjangoModelPermissionOrIsOwner,)
        elif self.action in ['terminate']:
            permission_classes = (ActionPermission,)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return job_models.Job.objects \
            .filter(owner=self.kwargs['employee_pk']) \
            .order_by('-timestamp')

    @atomic
    def create(self, request, *args, **kwargs):
        employee_id = self.kwargs['employee_pk']
        employee = get_object_or_404(core_models.Employee, pk=employee_id)
        serializer = job_serializer.JobSerializer(data=request.data, context={"employee": employee})
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        serializer.save()
        employee.current_job = serializer.instance
        employee.save()

        Q_Schedule.objects.filter(name=f"Deactive_Employee_{employee.pk}").delete()
        user = employee.user
        user.is_active = True
        user.save()

        return Response(data=serializer.data)

    @atomic
    @action(detail=False, methods=['post'])
    def terminate(self, request, *args, **kwargs):
        employee = get_object_or_404(core_models.Employee, pk=self.kwargs['employee_pk'])
        if not employee.is_working():
            return Response(status=status.HTTP_400_BAD_REQUEST, data="INACTIVE_EMPLOYEE")

        # Check job
        job = employee.get_current_job()
        serializer = job_serializer.TerminationSerializer(
            data=self.request.data,
            context={"job": job})

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        job.pk = None
        job.event = job_models.Job.JobEvent.Terminated
        job.save()

        serializer.save()

        employee.current_job = job
        employee.save()

        Q_Schedule.objects.create(
            func="qlns.apps.job.tasks.deactivate_employee",
            kwargs={"employee_id": employee.pk},
            name=f"Deactive_Employee_{employee.pk}",
            schedule_type=Q_Schedule.ONCE,
            next_run=job.termination.date,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
