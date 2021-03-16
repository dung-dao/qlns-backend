from rest_framework.viewsets import ModelViewSet
from qlns.apps.authentication.serializers import GroupSerializer
from django.contrib.auth.models import Group


class GroupView(ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    # permission_classes = ()
