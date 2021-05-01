from django.db import models


class TaxPolicy(models.Model):
    class TaxType(models.TextChoices):
        Progressive = 'Progressive'
        FixedPercentage = 'FixedPercentage'

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)
    tax_type = models.CharField(max_length=100, choices=TaxType.choices)
