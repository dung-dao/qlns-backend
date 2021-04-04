from rest_framework import views
from rest_framework import  permissions
from qlns.apps.core.models import Employee
from qlns.apps.core.serializers import CurrentUserSerializer
from rest_framework.response import Response
from django.core import exceptions
from rest_framework import status


class ProfileView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        try:
            employee = Employee.objects.filter(user=request.user).first()
            serializer = CurrentUserSerializer(instance=employee)
            return Response(data=serializer.data)
        except exceptions.ObjectDoesNotExist:
            return Response(data="No Profile")

    def post(self, request):
        employee = Employee.objects.filter(user=request.user).first()
        serializer = CurrentUserSerializer(
            instance=employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class ChangePasswordView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request):
        if 'password' not in request.data or 'new_password' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        password = request.data['password']
        new_password = request.data['new_password']

        user = request.user
        if user.check_password(password):
            user.set_password(new_password)
            user.save()
            return Response()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangeAvatarView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request):
        if 'avatar' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        employee = request.user.employee

        if employee is not  None:
            employee.avatar = request.data['avatar']
            employee.save()
            return Response()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="No Employee")
