from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAdminUser

from hrm_api.models import Department
from hrm_api.serializers import DepartmentSerializer


class DepartmentViewSet(ViewSet):
    permission_classes = (IsAdminUser, )

    def list(self, request):
        queryset = Department.objects.all()
        serializer = DepartmentSerializer(queryset, many=True)
        return Response(data=serializer.data)

    def create(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def retrieve(self, request, pk=None):
        item = get_object_or_404(Department, pk=pk)
        serializer = DepartmentSerializer(instance=item)
        return Response(data=serializer.data)

    def partial_update(self, request, pk=None):
        item = get_object_or_404(Department, pk=pk)
        serializer = DepartmentSerializer(
            instance=item, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request, pk=None):
        item = get_object_or_404(Department, pk=pk)
        item.delete()
        return Response(status=status.HTTP_200_OK)
