import xlwt
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
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
    def calculate(self, request, pk):
        payroll = Payroll.objects.filter(pk=pk).first()
        payroll.calculate_salary()

        return Response()

    @action(detail=True, methods=['get'])
    def export_excel(self, request, pk):
        payroll = Payroll.objects.filter(pk=pk).prefetch_related('payslips').first()
        if payroll is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        fields = payroll.template.fields.all()
        columns = list(map(lambda e: e.display_name, fields))

        # Prepare data
        payroll_name = payroll.name
        for sp in ['\\', '/', '*', '[', ']', ':', '?']:
            payroll_name = payroll_name.replace(sp, ' ').strip()

        payslips = payroll.payslips.all()
        wb = xlwt.Workbook(encoding='latin-1')

        worksheet = wb.add_sheet(payroll_name)

        header_style = xlwt.XFStyle()
        header_style.font.bold = True

        iter_row = 0

        title_style = xlwt.XFStyle()
        title_style.font.height = 16 * 16
        title_style.font.bold = True

        worksheet.write(iter_row, 0, payroll_name, title_style)

        iter_row += 2

        for col in range(len(columns)):
            worksheet.write(iter_row, col, columns[col], header_style)

        row_style = xlwt.XFStyle()

        iter_row += 1
        for payslip in payslips:
            values = list(map(lambda e: e.num_value if e.num_value is not None else e.str_value, payslip.values.all()))
            for i_val in range(len(values)):
                worksheet.write(iter_row, i_val, values[i_val], row_style)
            iter_row += 1

        # Response
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{payroll_name}.xls"'

        wb.save(response)
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
