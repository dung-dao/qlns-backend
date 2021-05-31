from django.db.models import Q
from django.db.transaction import atomic, set_rollback
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.attendance.models import TimeOff, Holiday
from qlns.apps.attendance.serializers import TimeOffSerializer
from qlns.apps.authentication.permissions import DjangoModelPermissionOrIsOwner, IsOwner, ActionPermission
from qlns.apps.core.models import Employee


class EmployeeTimeOffView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin
):
    queryset = TimeOff.objects.all()
    serializer_class = TimeOffSerializer

    def get_permissions(self):
        permission_classes = (permissions.IsAuthenticated,)
        if self.action in ('list',):
            permission_classes = (DjangoModelPermissionOrIsOwner,)
        elif self.action in ('cancel', 'create',):
            permission_classes = (IsOwner,)
        elif self.action in ('reject', 'approve',):
            permission_classes = (ActionPermission,)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return self.queryset.filter(owner=self.kwargs['employee_pk'])

    @atomic
    def create(self, request, *args, **kwargs):
        owner = self.request.user.employee
        employee = get_object_or_404(Employee, pk=self.kwargs.get('employee_pk'))
        schedule = employee.get_current_schedule()

        if schedule is None:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data="No Emplopyee Schedule")

        if owner.id != employee.pk:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Check if overlapped with approved time off

        start_date = request.data['start_date']
        end_date = request.data['end_date']
        overlapped = self.get_queryset().filter(
            (Q(start_date__gte=start_date) & Q(start_date__lte=end_date) |
             Q(end_date__gte=start_date) & Q(end_date__lte=end_date)) &
            Q(status=TimeOff.TimeOffStatus.Approved)
        ).exists()

        if overlapped:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="OVERLAPPED_WITH_ANOTHER_TIME_OFF")

        # Check if overlapped with a holiday
        holiday_overlapped = Holiday.objects.filter(
            Q(start_date__gte=start_date) & Q(start_date__lte=end_date) |
            Q(end_date__gte=start_date) & Q(end_date__lte=end_date)
        ).exists()
        if holiday_overlapped:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="OVERLAPPED_WITH_A_HOLIDAY")

        # TODO: check if time off is overlapped with approved attendance

        request_data = request.data
        context = {"owner": owner}
        serializer = TimeOffSerializer(data=request.data, context=context)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        serializer.save()
        created_time_off = serializer.data

        # Check if request time off that is not in schedule
        if created_time_off["work_hours"] == 0:
            set_rollback(True)
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data="time off in a not working day".strip().upper().replace(' ', '_'))
        return Response(data=serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, employee_pk, pk):
        time_off = self.get_queryset().filter(pk=pk).first()
        if time_off is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            time_off.status = TimeOff.TimeOffStatus.Canceled
            time_off.save()
        return Response(TimeOffSerializer(instance=time_off).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, employee_pk, pk):
        time_off = self.get_queryset().filter(pk=pk).first()
        if time_off is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Check status
        if time_off.status != TimeOff.TimeOffStatus.Pending:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Can only approve pending request")

        time_off.status = TimeOff.TimeOffStatus.Approved
        time_off.reviewed_by = self.request.user.employee
        time_off.save()
        return Response(TimeOffSerializer(instance=time_off).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, employee_pk, pk):
        time_off = self.get_queryset().filter(pk=pk).first()
        if time_off is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Check status
        if time_off.status != TimeOff.TimeOffStatus.Pending:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Can only reject pending request")

        time_off.status = TimeOff.TimeOffStatus.Rejected
        time_off.reviewed_by = self.request.user.employee
        time_off.save()
        return Response(TimeOffSerializer(instance=time_off).data)
