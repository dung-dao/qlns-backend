from rest_framework import status
from rest_framework.response import Response

from rest_framework import viewsets
from rest_framework import views
from rest_framework import permissions
from django.shortcuts import get_object_or_404


from django.contrib.auth.models import Group, Permission, User
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from qlns.apps.authentication.serializers import GroupSerializer, PermissionSerializer


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
