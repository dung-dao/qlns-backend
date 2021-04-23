from django.db import models


class OvertimeType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    point_rate = models.FloatField()
