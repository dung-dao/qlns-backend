from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from qlns.apps.core.models import Employee
from qlns.apps.core.serializers import EmployeeSerializer
from rest_framework.response import Response
from django.core import exceptions
from rest_framework import status
from django.contrib.auth.models import User


class ProfileView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        userid = request.user.id
        try:
            employee = Employee.objects.get(user=userid)
            serializer = EmployeeSerializer(instance=employee)
            return Response(data=serializer.data)
        except exceptions.ObjectDoesNotExist:
            return Response(data="No Profile")

    def post(self, request, format=None):
        userid = request.user.id
        serializer = None
        try:
            employee = Employee.objects.get(user=userid)
            serializer = EmployeeSerializer(
                instance=employee,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        except exceptions.ObjectDoesNotExist:
            request_data = request.data
            serializer = EmployeeSerializer(
                data=request_data,
                partial=True
            )
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

            else:
                employee = Employee(**request.data)
                user = User.objects.get(id=request.user.id)
                employee.user = user
                employee.save()
                return Response()
