from django.db import models


class AttendanceParam(models.Model):
    allow_outside = models.BooleanField()
