from django.db import models


class AttendanceCycle(models.Model):
    start_date = models.DateTimeField()
    approval_cycle = models.IntegerField()
