from django.db import models


class PayrollValue(models.Model):
    payroll = models.ForeignKey(to='Payroll', on_delete=models.CASCADE, related_name='values')
    field = models.ForeignKey(to='PayrollField', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=18, decimal_places=2)
