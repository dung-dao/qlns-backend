from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from django.contrib.auth.models import Group
from hrm_api.serializers import GroupSerializer, PermissionSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.status import \
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, \
    HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Permission


class RoleViewSet(ViewSet):
    permission_classes = (IsAdminUser, )

    def list(self, request):
        objs = Group.objects.all()
        serializer = GroupSerializer(objs, many=True)
        return Response(data=serializer.data)

    def retrieve(self, request, pk=None):
        try:
            group = Group.objects.get(pk=pk)
            serializer = GroupSerializer(group)
            return Response(status=HTTP_200_OK, data=serializer.data)
        except ObjectDoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            group = Group.objects.get(pk=pk)
            serializer = GroupSerializer(
                instance=group, data=request.data,  partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(status=HTTP_200_OK)
            else:
                return Response(status=HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            group = Group.objects.get(pk=pk)
            group.delete()
            return Response(status=HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
