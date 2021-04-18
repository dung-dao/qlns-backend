from django.db import models


class Schedule(models.Model):
    name = models.CharField(max_length=100, unique=True)
