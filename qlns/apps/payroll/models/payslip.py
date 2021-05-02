from django.db import models


class Payslip(models.Model):
    owner = models.ForeignKey(to='core.Employee', on_delete=models.CASCADE, related_name='payslips')
    payroll = models.ForeignKey(to='Payroll', on_delete=models.CASCADE, related_name='payslips')
