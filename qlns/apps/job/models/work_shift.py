from django.db import models


class WorkShift(models.Model):
    name = models.CharField(max_length=255, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()