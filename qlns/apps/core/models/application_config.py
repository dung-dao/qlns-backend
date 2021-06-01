from django.db import models


class ApplicationConfig(models.Model):
    # Attendance
    early_check_in_minutes = models.IntegerField(default=30)
    monthly_start_date = models.IntegerField(default=1)
    ot_point_rate = models.FloatField(default=1.5)
    require_face_id = models.BooleanField(default=False)
