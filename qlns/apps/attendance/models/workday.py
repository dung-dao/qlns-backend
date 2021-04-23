from django.db import models


class WorkDay(models.Model):
    class DayOfWeek(models.TextChoices):
        Monday = 'Mon'
        Tuesday = 'Tue'
        Wednesday = 'Wed'
        Thursday = 'Thu'
        Friday = 'Fri'
        Saturday = 'Sat'
        Sunday = 'Sun'

    # FK
    schedule = models.ForeignKey(to='Schedule', on_delete=models.CASCADE, related_name='workdays')

    # Fields
    day = models.CharField(max_length=3, choices=DayOfWeek.choices)

    morning_from = models.TimeField(blank=True, null=True)
    morning_to = models.TimeField(blank=True, null=True)

    afternoon_from = models.TimeField(blank=True, null=True)
    afternoon_to = models.TimeField(blank=True, null=True)
