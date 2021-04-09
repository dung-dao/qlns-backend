from django.db import models


class WorkExperience(models.Model):
    company = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    note = models.TextField(blank=True)
