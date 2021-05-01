from django.db import models


class SalarySystemField(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
