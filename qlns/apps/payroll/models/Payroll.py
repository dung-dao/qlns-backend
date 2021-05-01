from django.db import models


class Payroll(models.Model):
    template = models.ForeignKey(to='Template', on_delete=models.PROTECT)
    owner = models.ForeignKey(to='core.Employee', on_delete=models.CASCADE)
    cycle = models.ForeignKey(to='PayCycle', on_delete=models.PROTECT)

    # TODO: salary_info = models.ForeignKey(to='')
