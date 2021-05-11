from django.db import models


class InsurancePolicy(models.Model):
    class SalaryType(models.TextChoices):
        BasicSalary = 'Basic Salary'
        GrossSalary = 'Gross Salary'

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)
    base_on = models.CharField(max_length=100, choices=SalaryType.choices)
    percent_company = models.FloatField()
    percent_employee = models.FloatField()

