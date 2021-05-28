from django.db import models


class Payslip(models.Model):
    class Meta:
        default_permissions = ('view',)

    owner = models.ForeignKey(to='core.Employee', on_delete=models.CASCADE, related_name='payslips')
    payroll = models.ForeignKey(to='Payroll', on_delete=models.CASCADE, related_name='payslips')
