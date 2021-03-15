from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from hrm_api.models import Staff
from hrm_api.serializers import StaffSerializer
from django.core.exceptions import ObjectDoesNotExist


class StaffViewSet(ViewSet):
    permission_classes = (IsAdminUser, )

    def list(self, request):
        queryset = Staff.objects.all()
        serializer = StaffSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        staff = get_object_or_404(Staff, pk=pk)
        serializer = StaffSerializer(staff)
        return Response(serializer.data)

    def create(self, request):
        serializer = StaffSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data=serializer.data)

    def update(self, request, pk=None):
        staff = get_object_or_404(Staff, pk=pk)
        serializer = StaffSerializer(
            instance=staff, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def partial_update(self, request, pk=None):
        staff = get_object_or_404(Staff, pk=pk)
        serializer = StaffSerializer(
            instance=staff, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request, pk=None):
        staff = get_object_or_404(Staff, pk=pk)
        staff.delete()
        return Response(status=status.HTTP_200_OK)
