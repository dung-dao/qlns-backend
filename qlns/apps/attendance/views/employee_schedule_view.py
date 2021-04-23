from rest_framework import viewsets, status
from rest_framework.response import Response

from qlns.apps.attendance.models import EmployeeSchedule
from qlns.apps.attendance.serializers.employee_schedule import EmployeeScheduleSerializer


class EmployeeScheduleView(viewsets.ViewSet):
    serializer_class = EmployeeScheduleSerializer

    def get_queryset(self):
        return EmployeeSchedule.objects.filter(owner=self.kwargs['employee_pk'])

    def list(self, request, employee_pk=None):
        schedule = self.get_queryset().first()
        if schedule is not None:
            serializer = EmployeeScheduleSerializer(instance=schedule)
            return Response(data=serializer.data)
        else:
            return Response(data={})

    def create(self, request, employee_pk=None):
        schedule = self.get_queryset().first()

        serializer = None
        if schedule is None:
            serializer = self.serializer_class(data=request.data)
        else:
            serializer = self.serializer_class(
                instance=schedule, data=request.data)

        if serializer.is_valid():
            if str(request.data['owner']) != employee_pk:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            return Response(data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
