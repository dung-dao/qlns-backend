from django.db import models


class PayCycle(models.Model):
    name = models.CharField(max_length=255, unique=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
