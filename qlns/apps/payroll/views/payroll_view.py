import io

import xlsxwriter
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.transaction import atomic
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.attendance.models import Period
from qlns.apps.payroll.models import Payroll
from qlns.apps.payroll.serializers.payroll_serializer import PayrollSerializer


class PayrollView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
):
    # permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PayrollSerializer
    queryset = Payroll.objects.all()

    def create(self, request, *args, **kwargs):
        ctx = {"request": request, "period": request.data.get('period', None)}
        if ctx['period'] is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="period required")

        period = get_object_or_404(Period, pk=ctx['period'])
        ctx['period'] = period

        serializer = PayrollSerializer(data=request.data, context=ctx)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk):
        payroll = get_object_or_404(Payroll, pk=pk)
        payroll.status = Payroll.Status.Confirmed
        payroll.save()
        return Response()

    @atomic
    @action(detail=True, methods=['post'])
    def calculate(self, request, pk):
        payroll = get_object_or_404(Payroll, pk=pk)
        if payroll.status == Payroll.Status.Confirmed:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Cannot modify confirmed payroll")
        try:
            payroll.calculate_salary()
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid template")
        return Response()

    @action(detail=True, methods=['get'])
    def export_excel(self, request, pk):
        payroll = Payroll.objects.filter(pk=pk).prefetch_related('payslips').first()
        if payroll is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Headers
        fields = list(payroll.template.fields.all())
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
                'font_name': 'Times New Roman',
            }
        )

        normal_style = wb.add_format(
            {
                'font_size': 13,
                'bold': False,
                'font_name': 'Times New Roman',
            }
        )

        title_style = wb.add_format(
            {
                'font_size': 16,
                'font_name': 'Times New Roman',
            }
        )

        normal_cell_style = wb.add_format(
            {
                'font_size': 13,
                'bold': False,
                'font_name': 'Times New Roman',
                'border': 1,
            }
        )

        currency_cell_style = wb.add_format(
            {
                'num_format': '#,##0₫',
                'font_size': 13,
                'bold': False,
                'font_name': 'Times New Roman',
                'border': 1,
            }
        )

        # Write title
        worksheet.write(0, 0, payroll_name, title_style)

        # Write headers
        for col in range(len(column_names)):
            worksheet.write(2, col, column_names[col], header_style)

        # Write data rows
        i_row = 3
        for payslip in payslips:
            values = payslip.values.all().order_by('field__index')
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
            values = list(map(
                lambda e: {
                    'name': e.field.display_name,
                    'value': e.num_value if e.num_value is not None else e.str_value
                },
                payslip.values.all().order_by('field__index')))

            payroll_name = 'Phiếu lương tháng 4 2021'
            payslip_name = f'Phiếu lương {payroll.period.start_date.month}/{payroll.period.start_date.year}'

            html_context = {
                'title': payslip_name,
                'values': values,
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
