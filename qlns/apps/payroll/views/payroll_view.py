import io
import math

import xlsxwriter
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.transaction import atomic, set_rollback
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from formulas.errors import FormulaError
from rest_framework import status, permissions
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.attendance.models import Period
from qlns.apps.authentication.permissions import ActionPermission
from qlns.apps.payroll.models import Payroll
from qlns.apps.payroll.models.payroll import InputFileError
from qlns.apps.payroll.serializers.payroll_serializer import PayrollSerializer
from qlns.utils.datetime_utils import to_date_string


class PayrollView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = PayrollSerializer
    queryset = Payroll.objects.all()

    def get_permissions(self):
        permission_classes = (permissions.IsAuthenticated,)
        if self.action in ('list', 'create', 'destroy'):
            permission_classes = (permissions.DjangoModelPermissions,)
        elif self.action in ('calculate', 'export_excel', 'send_payslip', 'confirm',):
            permission_classes = (ActionPermission,)

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        ctx = {"request": request, "period": request.data.get('period', None)}
        if ctx['period'] is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="period required")

        period = get_object_or_404(Period, pk=ctx['period'])
        ctx['period'] = period

        serializer = PayrollSerializer(data=request.data, context=ctx)
        if serializer.is_valid():
            serializer.save()
            payroll = serializer.instance

            try:
                payroll.calculate_salary()
            except FormulaError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid template")
            return Response(data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        payroll = get_object_or_404(Payroll, pk=pk)

        if payroll.status == Payroll.Status.Confirmed:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Cannot delete confirmed payroll")
        else:
            payroll.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk):
        payroll = get_object_or_404(Payroll, pk=pk)
        if payroll.status != Payroll.Status.Confirmed:
            payroll.status = Payroll.Status.Confirmed
            payroll.confirmed_by = request.user.employee
            payroll.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Already confirmed")

    @atomic
    @action(detail=True, methods=['post'])
    def calculate(self, request, pk):
        payroll = get_object_or_404(Payroll, pk=pk)
        if payroll.status == Payroll.Status.Confirmed:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Cannot modify confirmed payroll")
        try:
            payroll.calculate_salary()
        except FormulaError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid template")
        return Response()

    @action(detail=True, methods=['get'])
    def inputs_template(self, request, pk):
        user = request.user
        has_perm = user.has_perm('payroll.view_payroll')
        if not has_perm:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        payroll = get_object_or_404(Payroll, pk=pk)
        if payroll.status == Payroll.Status.Confirmed:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Cannot modify confirmed payroll")

        fields = list(payroll.template.fields
                      .filter(type='Input')
                      .order_by('index'))
        column_names = list(map(lambda e: e.display_name, fields))
        column_width = list(map(lambda s: len(s) + 4, column_names))

        # Inject employee fields
        column_names.insert(0, "Id")
        column_names.insert(1, "H??? t??n")

        column_width.insert(0, len("Id"))
        column_width.insert(1, len("H??? t??n"))


        # Create workbook
        payroll_name = payroll.name
        for sp in ['\\', '/', '*', '[', ']', ':', '?']:
            payroll_name = payroll_name.replace(sp, ' ').strip()

        payroll_name = "D??? li???u b??? sung"
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output)

        worksheet = wb.add_worksheet(payroll_name)

        # Styles
        header_style = wb.add_format(
            {
                'bold': True,
                'font_size': 13,
                'align': 'center',
                'border': 1,
                'bg_color': '#f2f2f2',
            }
        )

        normal_style = wb.add_format(
            {
                'font_size': 13,
                'bold': False,
            }
        )

        no_border_cell_style = wb.add_format(
            {
                'font_size': 13,
                'bold': False,
                'border': 0,
            }
        )

        title_style = wb.add_format(
            {
                'font_size': 16,
                'bold': True,
            }
        )

        normal_cell_style = wb.add_format(
            {
                'font_size': 13,
                'bold': False,
                'border': 1,
            }
        )

        currency_cell_style = wb.add_format(
            {
                'num_format': '#,##0???',
                'font_size': 13,
                'bold': False,
                'border': 1,
            }
        )

        locked = wb.add_format()
        locked.set_locked(True)

        # Write title
        worksheet.write(0, 0, payroll_name, title_style)
        worksheet.set_row(0, 24)

        # Write headers
        for col in range(len(column_names)):
            worksheet.write(3, col, column_names[col], header_style)

        worksheet.write(1, 0,
                        f"Chu k??? l????ng: {to_date_string(payroll.period.start_date)} - {to_date_string(payroll.period.end_date)}")

        # Write data rows
        i_row = 4
        employees = payroll.get_payroll_employees()
        for em_index in range(len(employees)):
            employee = employees[em_index]
            worksheet.write(i_row + em_index, 0, employee.pk, no_border_cell_style)
            worksheet.write(i_row + em_index, 1, employee.full_name, no_border_cell_style)

            # if the length of the cell's content is wider than the current column width, widen the column width

            # because only two columns (0:employee.pk, 1:employee.full_name) have content, we only 
            # need to take care of them, cause this is an "input TEMPLATE", the other columns are all empty already
            if len(str(employee.pk)) > column_width[0]:
                column_width[0] = len(str(employee.pk))
            if len(str(employee.full_name)) > column_width[1]:
                column_width[1] = len(str(employee.full_name))

        # We have built the "column_width" dictionary, now using it to actually set the width of the columns
        for col in range(len(column_names)):
            worksheet.set_column(col, col, column_width[col] + 4)

        # Response
        wb.close()
        output.seek(0)
        filename = payroll_name
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s.xlsx' % filename

        return response

    @atomic
    @action(detail=True, methods=['post'])
    def upload_inputs(self, request, pk):
        user = request.user
        has_perm = user.has_perm('payroll.change_payroll') or user.has_perm('payroll.add_payroll')
        if not has_perm:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        payroll = get_object_or_404(Payroll, pk=pk)
        if payroll.status == Payroll.Status.Confirmed:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Cannot modify confirmed payroll")

        if not payroll.is_inputs_file_required():
            return Response(status=status.HTTP_400_BAD_REQUEST, data="No input field")

        file = request.data.get('input_file', None)
        if file is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="input_file required!")

        payroll.input_file = file
        payroll.save()
        try:
            payroll.calculate_salary()
        except InputFileError:
            set_rollback(True)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Data error in excel file"})
        return Response()

    @action(detail=True, methods=['get'])
    def export_excel(self, request, pk):
        payroll = Payroll.objects.filter(pk=pk).prefetch_related('payslips').first()
        if payroll is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Headers
        fields = list(payroll.template.fields.filter(is_visible=True).order_by('index'))
        column_names = list(map(lambda e: e.display_name, fields))
        column_width = list(map(lambda s: len(s), column_names))

        # Prepare data
        payroll_name = payroll.name
        for sp in ['\\', '/', '*', '[', ']', ':', '?']:
            payroll_name = payroll_name.replace(sp, ' ').strip()

        payslips = payroll.payslips.prefetch_related('values').all()

        # Create workbook
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output)

        worksheet = wb.add_worksheet(payroll_name)

        # Styles
        header_style = wb.add_format(
            {
                'bold': True,
                'font_size': 13,
                'align': 'center',
                'border': 1,
                'bg_color': '#f2f2f2',
            }
        )

        normal_style = wb.add_format(
            {
                'font_size': 13,
                'bold': False,
            }
        )

        title_style = wb.add_format(
            {
                'font_size': 16,
                'bold': True,
            }
        )

        normal_cell_style = wb.add_format(
            {
                'font_size': 13,
                'bold': False,
                'border': 1,
            }
        )

        currency_cell_style = wb.add_format(
            {
                'num_format': '#,##0???',
                'font_size': 13,
                'bold': False,
                'border': 1,
            }
        )

        # Write title
        worksheet.write(0, 0, payroll_name, title_style)
        worksheet.set_row(0, 24)

        # Write headers
        for col in range(len(column_names)):
            worksheet.write(3, col, column_names[col], header_style)

        worksheet.write(1, 0,
                        f"Chu k??? l????ng: {to_date_string(payroll.period.start_date)} - {to_date_string(payroll.period.end_date)}")

        # Write data rows
        i_row = 4
        for payslip in payslips:
            values = payslip.values.filter(field__is_visible=True).order_by('field__index')
            for i_val in range(values.count()):
                value = None
                cell_style = None

                if values[i_val].field.datatype == 'Text':
                    value = values[i_val].str_value
                    cell_style = normal_cell_style

                elif values[i_val].field.datatype == 'Number' or \
                        values[i_val].field.datatype == 'Currency':
                    value = values[i_val].num_value
                    cell_style = currency_cell_style
                if len(str(value)) > column_width[i_val]:
                    column_width[i_val] = len(str(value))
                worksheet.write(i_row, i_val, value, cell_style)
            i_row += 1

        for col in range(len(column_names)):
            worksheet.set_column(col, col, column_width[col] + 4)

        wb.close()

        # Response
        output.seek(0)
        filename = payroll_name
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s.xlsx' % filename

        return response

    @action(detail=True, methods=['post'])
    def send_payslip(self, request, pk):
        payroll = Payroll.objects.filter(pk=pk).prefetch_related('payslips').first()
        if payroll is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        for payslip in payroll.payslips.all():
            email_address = payslip.owner.email

            def map_value(e):
                value = None
                if e.num_value is not None:
                    raw_value = e.num_value
                    if math.floor(raw_value) - raw_value == 0:
                        value = int(e.num_value)
                    else:
                        value = e.num_value
                    value = f'{value:,}'
                else:
                    value = e.str_value
                return {
                    'name': e.field.display_name,
                    'value': value if e.field.datatype != "Currency" else str(f'{int(e.num_value):,}') + ' ???'
                }

            _payslip_values = payslip.values.select_related('field') \
                .filter(field__is_visible=True) \
                .order_by('field__index')
            values = list(map(map_value, _payslip_values))

            period_start_date = timezone.localtime(payroll.period.start_date)

            payroll_name = f'Th??ng b??o th??ng tin b???ng l????ng {period_start_date.month}/{period_start_date.year}'
            payslip_name = f'Phi???u l????ng {period_start_date.month}/{period_start_date.year}'

            html_context = {
                'title': payslip_name,
                'values': values,
                'cycle_start_date': to_date_string(payroll.period.start_date),
                'cycle_end_date': to_date_string(payroll.period.end_date),
                'hostname': ''.join(['http://', request.get_host()])
            }

            payslip_content = render_to_string('email_payslip.html', html_context)
            payslip_text = strip_tags(payslip_content)
            email = EmailMultiAlternatives(
                payroll_name,
                payslip_text,
                settings.EMAIL_HOST_USER,
                [email_address]
            )
            email.attach_alternative(payslip_content, 'text/html')
            email.send()
        return Response()
