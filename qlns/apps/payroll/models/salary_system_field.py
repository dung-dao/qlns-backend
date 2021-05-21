from django.db import models


class SalarySystemField(models.Model):
    class Datatype(models.TextChoices):
        Number = 'Number'
        Currency = 'Currency'
        Text = 'Text'

    name = models.CharField(max_length=255, unique=True)
    code_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    datatype = models.CharField(max_length=20, choices=Datatype.choices)
