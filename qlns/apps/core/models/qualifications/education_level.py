from django.db import models


class EducationLevel(models.Model):
    name = models.CharField(max_length=150, unique=True)