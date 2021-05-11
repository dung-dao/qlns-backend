from django.db import models


class SalaryTemplate(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_default = models.BooleanField(default=False)
