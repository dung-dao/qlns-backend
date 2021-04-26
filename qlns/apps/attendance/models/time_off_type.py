from django.db import models


class TimeOffType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_paid = models.BooleanField()
    description = models.TextField(blank=True, null=True)
