import re

from django.db import transaction
from django.db.models import ProtectedError
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from formulas.errors import FormulaError
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.payroll.models import SalaryTemplate, SalaryTemplateField
from qlns.apps.payroll.serializers.salary_template_field_serializer import SalaryTemplateFieldSerializer
from qlns.apps.payroll.serializers.salary_template_serializer import SalaryTemplateSerializer


class DuplicateSalaryTemplatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('payroll.add_salarytemplate')


class SalaryTemplateView(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SalaryTemplateSerializer
    queryset = SalaryTemplate.objects.prefetch_related('fields').all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'destroy', 'update']:
            permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
        elif self.action == 'get_system_fields':
            permission_classes = ()
        elif self.action == 'duplicate':
            permission_classes = (DuplicateSalaryTemplatePermission,)
        else:
            raise Exception('Unreachable code')
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def get_system_fields(self, request):
        system_fields = SalaryTemplateField.objects.filter(
            type=SalaryTemplateField.SalaryFieldType.SystemField
        )
        list_serializer = SalaryTemplateFieldSerializer(system_fields, many=True)
        return Response(data=list_serializer.data)

    @atomic
    def update(self, request, pk=None):
        template = SalaryTemplate.objects.filter(pk=pk) \
            .prefetch_related('payrolls') \
            .first()
        if template is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if template.payrolls \
                .filter(status='Confirmed') \
                .exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Denied")

        serializer = self.serializer_class(instance=template, data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        serializer.save()

        try:
            for p in template.payrolls.all():
                p.calculate_salary()
        except FormulaError:
            transaction.set_rollback(True)
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid formula")

        return Response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            return super(SalaryTemplateView, self).destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Denied")

    @atomic
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        template = get_object_or_404(SalaryTemplate, pk=pk)
        fields = template.fields.all()

        template.pk = None
        template.is_default = False

        # Old solution
        # old_name = template.name
        # index = 1
        #
        # while SalaryTemplate.objects.filter(name=old_name + f' ({index})').exists() and \
        #         SalaryTemplate.objects.filter(name=old_name):
        #     index = index + 1
        #
        # template.name = old_name + f' ({index})'

        # New solution
        old_name = template.name
        num = 1

        last_duplicate_template = SalaryTemplate.objects \
            .filter(name__iregex=fr'{template.name} \([0-9]+\)') \
            .order_by('-name') \
            .first()

        if last_duplicate_template is not None:
            num_str = re.search(r'\([0-9]+\)(?!.*\([0-9]+\))', last_duplicate_template.name).group(0)
            num = int(num_str.replace('(', '').replace(')', '')) + 1

        template.name = request.data.get('name',  old_name + f' ({num})')

        template.save()

        for field in fields:
            field.pk = None
            field.template = template
            field.save()

        serializer = SalaryTemplateSerializer(instance=template)
        return Response(data=serializer.data)
