from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from qlns.apps.authentication.permissions import RWPermissionOrViewOwn
from qlns.apps.core.models import Employee
from qlns.apps.payroll.models import EmployeeSalary
from qlns.apps.payroll.serializers.employee_salary_serializer import EmployeeSalarySerializer


class EmployeeSalaryView(viewsets.ViewSet):
    serializer_class = EmployeeSalarySerializer
    permission_classes = (RWPermissionOrViewOwn,)

    def get_queryset(self):
        return EmployeeSalary.objects.filter(owner=self.kwargs['employee_pk'])

    def list(self, request, employee_pk=None):
        salary_config = self.get_queryset().first()
        if salary_config is not None:
            serializer = self.serializer_class(instance=salary_config)
            return Response(data=serializer.data)
        else:
            return Response(data={})

    def create(self, request, employee_pk=None):
        salary_info = self.get_queryset().first()
        owner = Employee.objects.filter(pk=self.kwargs['employee_pk']).first()

        serializer = None
        if salary_info is None:
            serializer = self.serializer_class(
                data=request.data,
                context={"request": request, "owner": owner}
            )
        else:
            serializer = self.serializer_class(
                instance=salary_info, data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
