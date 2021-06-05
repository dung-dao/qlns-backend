from django.db import models


class PayslipValue(models.Model):
    class Meta:
        default_permissions = ()

    payslip = models.ForeignKey(to='Payslip', on_delete=models.CASCADE, related_name='values')
    field = models.ForeignKey(to='SalaryTemplateField', on_delete=models.CASCADE)

    num_value = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    str_value = models.CharField(max_length=1000, null=True)

    def get_formatted_value(self):
        # String data doesn't need to be formatted
        if self.str_value is not None:
            return self.str_value

        # Format currency
        if self.num_value is not None:
            if self.field.datatype == 'Currency':
                return f'{self.num_value:,}'
            return str(self.num_value)
