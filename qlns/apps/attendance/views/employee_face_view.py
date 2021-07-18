from django.db.transaction import atomic, set_rollback
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response

from qlns.apps.attendance.models import EmployeeFace
from qlns.apps.attendance.serializers import EmployeeFaceSerializer
from qlns.apps.attendance.services.face_services import add_recognition_image, remove_recognition_image, create_person
from qlns.apps.authentication.permissions import CRUDPermission
from qlns.apps.core.models import Employee


class EmployeeFaceView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin
):
    queryset = EmployeeFace.objects.all()
    serializer_class = EmployeeFaceSerializer
    permission_classes = (CRUDPermission,)

    def get_queryset(self):
        try:
            return self.queryset.filter(owner=self.kwargs['employee_pk']) \
                .order_by('-timestamp')
        except ValueError:
            return EmployeeFace.objects.none()

    @atomic
    def create(self, request, *args, **kwargs):
        employee_pk = int(self.kwargs['employee_pk'])
        employee = get_object_or_404(Employee, pk=employee_pk)

        if employee.recognition_id is None:
            employee.recognition_id = create_person(employee.full_name)
            employee.save()

        image = request.data['image'].file.read()
        face_id = add_recognition_image(employee.recognition_id, image)
        request.data['image'].file.seek(0)

        if face_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        context = {
            "request": request,
            "employee": employee,
            "face_id": face_id
        }

        serializer = EmployeeFaceSerializer(data=request.data,
                                            context=context)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        serializer.save()
        return Response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        pk = int(kwargs.get('pk', -1))
        employee_pk = int(self.kwargs['employee_pk'])
        employee = get_object_or_404(Employee, pk=employee_pk)

        face = self.queryset.filter(pk=pk).first()
        if face is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        face_id = face.azure_face_id
        remove_recognition_image(employee.recognition_id, face_id)
        face.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
