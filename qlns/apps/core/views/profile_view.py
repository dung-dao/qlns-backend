from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from qlns.apps.core.models import Employee
from qlns.apps.core.serializers import CurrentUserSerializer
from rest_framework.response import Response
from django.core import exceptions
from rest_framework import status
from django.contrib.auth.models import User


class ProfileView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            employee = Employee.objects.filter(user=request.user).first()
            serializer = CurrentUserSerializer(instance=employee)
            return Response(data=serializer.data)
        except exceptions.ObjectDoesNotExist:
            return Response(data="No Profile")

    def post(self, request, format=None):
        employee = Employee.objects.filter(user=request.user).first()
        serializer = CurrentUserSerializer(
            instance=employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
