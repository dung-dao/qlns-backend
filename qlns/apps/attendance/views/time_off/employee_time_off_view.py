from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from qlns.apps.attendance.models import TimeOff, Holiday
from qlns.apps.attendance.serializers import TimeOffSerializer
from qlns.apps.core.models import Employee


class EmployeeTimeOffView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin
):
    permission_classes = (IsAuthenticated,)
    queryset = TimeOff.objects.all()
    serializer_class = TimeOffSerializer

    def get_queryset(self):
        return self.queryset.filter(owner=self.kwargs['employee_pk'])

    def create(self, request, *args, **kwargs):
        owner = self.request.user.employee
        employee = get_object_or_404(Employee, pk=self.kwargs.get('employee_pk'))

        if owner.id != employee.pk:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Check overlapped time off
        # => Check if there is a time off that has start_date or end_date between incoming start_date and end_date

        start_date = request.data['start_date']
        end_date = request.data['end_date']
        overlapped = self.get_queryset().filter(
            Q(start_date__gte=start_date) & Q(start_date__lte=end_date) |
            Q(end_date__gte=start_date) & Q(end_date__lte=end_date)
        ).exists()

        if overlapped:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="OVERLAPPED_WITH_ANOTHER_TIME_OFF")

        # Check holiday
        holiday_overlapped = Holiday.objects.filter(
            Q(start_date__gte=start_date) & Q(start_date__lte=end_date) |
            Q(end_date__gte=start_date) & Q(end_date__lte=end_date)
        ).exists()
        if holiday_overlapped:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="OVERLAPPED_WITH_A_HOLIDAY")

        # Check Saturday, Sunday (schedule)

        context = {"owner": owner}
        serializer = TimeOffSerializer(data=request.data, context=context)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        serializer.save()
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
