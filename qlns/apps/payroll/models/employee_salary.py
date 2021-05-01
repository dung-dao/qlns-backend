from django.db import models


class EmployeeSalary(models.Model):
    owner = models.ForeignKey(to='core.Employee', on_delete=models.CASCADE, related_name='salary_info')
    insurance_policy = models.ForeignKey(to='InsurancePolicy', on_delete=models.PROTECT)
    tax_policy = models.ForeignKey(to='TaxPolicy', on_delete=models.PROTECT)
    salary = models.DecimalField(max_digits=18, decimal_places=2)
