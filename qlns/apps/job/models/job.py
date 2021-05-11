from django.db import models


class Job(models.Model):
    class JobEvent(models.TextChoices):
        Error_Correction = 'Error Correction'
        Joined = 'Joined'
        Location_Changed = 'Location Changed'
        Other = 'Other'
        Promoted = 'Promoted'
        Terminated = 'Terminated'

    owner = models.ForeignKey(
        to='core.Employee', on_delete=models.CASCADE, related_name='job_history')
    job_title = models.ForeignKey(to='JobTitle', on_delete=models.PROTECT, related_name='jobs')
    location = models.ForeignKey(to='Location', on_delete=models.PROTECT, related_name='jobs')
    employment_status = models.ForeignKey(to='EmploymentStatus', on_delete=models.PROTECT)

    department = models.ForeignKey(to='core.Department', on_delete=models.SET_NULL, null=True, related_name='jobs')
    probation_start_date = models.DateField(blank=True, null=True)
    probation_end_date = models.DateField(blank=True, null=True)
    contract_start_date = models.DateField(blank=True, null=True)
    contract_end_date = models.DateField(blank=True, null=True)

    # Termination info
    is_terminated = models.BooleanField(default=False)
    termination_reason = models.CharField(max_length=255, null=True)
    termination_date = models.DateTimeField(null=True)
    termination_note = models.CharField(max_length=1000, null=True, blank=True)

    event = models.CharField(max_length=100, choices=JobEvent.choices, default=JobEvent.Joined)
    timestamp = models.DateTimeField(auto_now_add=True)
