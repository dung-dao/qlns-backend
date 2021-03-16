from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from qlns.apps.authentication.serializers import GroupSerializer, PermissionSerializer
from django.contrib.auth.models import Group, Permission
from rest_framework.permissions import IsAdminUser, IsAuthenticated


class GroupView(ModelViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = GroupSerializer
    queryset = Group.objects.all()


class PermissionView(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
