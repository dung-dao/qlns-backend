from django.db import models


class PayrollConfig(models.Model):
    use_check_in = models.BooleanField()
    monthly_start_date = models.IntegerField()
