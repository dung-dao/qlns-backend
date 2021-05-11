from django.db import models


class PayslipValue(models.Model):
    payslip = models.ForeignKey(to='Payslip', on_delete=models.CASCADE, related_name='values')
    field = models.ForeignKey(to='SalaryTemplateField', on_delete=models.CASCADE)

    num_value = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    str_value = models.CharField(max_length=1000, null=True)
