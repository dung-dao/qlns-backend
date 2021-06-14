from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from rest_framework import views
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response

from qlns.apps.authentication.serializers import GroupSerializer, PermissionSerializer, PermissionStatusSerializer


class GroupView(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    def get_permissions(self):
        permission_classes = (DjangoModelPermissions,)
        return [permission() for permission in permission_classes]


class PermissionView(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return Permission.objects.filter(
            ~Q(content_type__app_label='admin') &
            ~Q(content_type__app_label='sessions') &
            ~Q(content_type__app_label='contenttypes') &
            ~Q(content_type__model='permission') &
            ~Q(content_type__app_label='django_q')) \
            .select_related('content_type') \
            .order_by('id')

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class AuthenticatedPermissionView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        permissions = ()
        all_permissions = Permission.objects.filter(
            ~Q(content_type__app_label='admin') &
            ~Q(content_type__app_label='sessions') &
            ~Q(content_type__app_label='contenttypes') &
            ~Q(content_type__model='permission') &
            ~Q(content_type__app_label='django_q')) \
            .select_related('content_type') \
            .order_by('id')

        user = request.user
        if user.is_superuser:
            permissions = all_permissions
        else:
            permissions = user.user_permissions.all() | Permission.objects.filter(group__user=user)

        def map_permission_to_perm_status(perm):
            return {'id': perm.id,
                    'name': perm.name,
                    'codename': perm.codename,
                    'content_type': perm.content_type.name,
                    'has_perm': perm in permissions}

        permission_statuses = list(map(map_permission_to_perm_status, all_permissions))
        serializer = PermissionStatusSerializer(instance=permission_statuses, many=True)
        return Response(data=serializer.data)
