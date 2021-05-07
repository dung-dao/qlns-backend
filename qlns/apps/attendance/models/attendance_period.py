from django.db import models


class AttendancePeriod(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
