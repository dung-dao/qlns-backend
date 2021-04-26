from django.db import models


class TimeOff(models.Model):
    class TimeOffStatus(models.TextChoices):
        Pending = 'Pending'
        Canceled = 'Canceled'
        Approved = 'Approved'
        Rejected = 'Rejected'

    owner = models.ForeignKey(to='core.Employee', on_delete=models.CASCADE,
                              related_name='TimeOff')
    reviewed_by = models.ForeignKey(to='core.Employee', on_delete=models.SET_NULL,
                                    null=True, related_name='ReviewedTimeOff')
    time_off_type = models.ForeignKey(to='TimeOffType', on_delete=models.PROTECT,
                                      related_name='TimeOff')

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    status = models.CharField(max_length=15, choices=TimeOffStatus.choices)
    note = models.TextField(blank=True, null=True)
