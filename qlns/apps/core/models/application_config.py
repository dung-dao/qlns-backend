from django.db import models


class ApplicationConfig(models.Model):
    # Attendance
    monthly_start_date = models.IntegerField(default=1)
