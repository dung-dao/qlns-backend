from django.contrib.auth.models import Group, Permission
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
    all_perm_str_query = "SELECT DISTINCT perm.* FROM auth_permission perm LEFT JOIN qlns.django_content_type " \
                         "ctt ON perm.content_type_id = ctt.id WHERE NOT ctt.app_label='admin' AND NOT " \
                         "ctt.app_label='sessions' AND NOT ctt.app_label='contenttypes' AND NOT ctt.app_label='admin' " \
                         "AND NOT ctt.app_label='django_q' ORDER BY perm.id "

    def get_queryset(self):
        return Permission.objects.raw(self.all_perm_str_query)

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class AuthenticatedPermissionView(views.APIView):
    permission_classes = (IsAuthenticated,)

    all_perm_str_query = "SELECT DISTINCT perm.* FROM auth_permission perm LEFT JOIN qlns.django_content_type " \
                         "ctt ON perm.content_type_id = ctt.id WHERE NOT ctt.app_label='admin' AND NOT " \
                         "ctt.app_label='sessions' AND NOT ctt.app_label='contenttypes' AND NOT ctt.app_label='admin' " \
                         "AND NOT ctt.app_label='django_q' ORDER BY perm.id "

    def get(self, request, format=None):
        all_permissions = Permission.objects.raw(self.all_perm_str_query)
        permissions = ()
        user = request.user
        if user.is_superuser:
            permissions = all_permissions
        else:
            permissions = user.user_permissions.all() | Permission.objects.filter(group__user=user)

        def map_permission_to_perm_status(perm):
            return {'id': perm.id,
                    'name': perm.name,
                    'codename': perm.codename,
                    'has_perm': perm in permissions}

        permission_statuses = list(map(map_permission_to_perm_status, all_permissions))
        serializer = PermissionStatusSerializer(instance=permission_statuses, many=True)
        return Response(data=serializer.data)
