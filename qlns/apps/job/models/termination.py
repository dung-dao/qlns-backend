from django.db import models


class Termination(models.Model):
    job = models.OneToOneField(to='job.Job', on_delete=models.CASCADE, related_name='termination')
    reason = models.ForeignKey(to='TerminationReason', on_delete=models.PROTECT, related_name='termination')
    date = models.DateTimeField()
    note = models.TextField(null=True, blank=True)
