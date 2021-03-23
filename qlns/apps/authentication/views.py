from rest_framework import status
from rest_framework.response import Response

from rest_framework import viewsets
from rest_framework import views
from rest_framework import permissions
from django.shortcuts import get_object_or_404


from django.contrib.auth.models import Group, Permission
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from qlns.apps.authentication.serializers import GroupSerializer, PermissionSerializer, EmployeeSerializer, CountrySerializer
from qlns.apps.authentication.models import User, Employee, Country


class GroupView(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = GroupSerializer
    queryset = Group.objects.all()


class PermissionView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class AuthenticatedPermissionView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        queryset = []
        user = request.user
        if user.is_superuser:
            queryset = Permission.objects.all()
        else:
            queryset = user.user_permissions.all()
        res = PermissionSerializer(instance=queryset, many=True)
        return Response(data=res.data)


class EmployeeView(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Employee.objects.filter(user__is_active=True)
    serializer_class = EmployeeSerializer

    def destroy(self, request, pk=None):
        employee = get_object_or_404(Employee, pk=pk)
        user = employee.user
        user.is_active = False
        user.save()
        return Response()

    def partial_update(self, request, pk=None):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(
            instance=employee, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class ProfileView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        userid = request.user.id
        employee = Employee.objects.get(user=userid)
        serializer = EmployeeSerializer(instance=employee)

        return Response(data=serializer.data)

    def post(self, request, format=None):
        userid = request.user.id
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


class CountryView(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
