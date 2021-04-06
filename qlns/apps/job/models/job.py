from django.db import models


class Job(models.Model):
    class EmploymentStatus(models.TextChoices):
        onboarding = 'Onboarding'
        probationary = 'Probationary'
        active = 'Active'
        on_leave = 'On Leave'

    owner = models.ForeignKey(
        to='core.Employee', on_delete=models.CASCADE, related_name='job_history')
    department = models.ForeignKey(to='core.Department', on_delete=models.SET_NULL, null=True, related_name='jobs')
    job_title = models.ForeignKey(to='JobTitle', on_delete=models.SET_NULL, null=True, related_name='jobs')
    work_shift = models.ForeignKey(to='WorkShift', on_delete=models.SET_NULL, null=True, related_name='jobs')
    location = models.ForeignKey(to='Location', on_delete=models.SET_NULL, null=True, related_name='jobs')

    employment_status = models.CharField(max_length=20, choices=EmploymentStatus.choices)
    probation_start_date = models.DateField(blank=True, null=True)
    probation_end_date = models.DateField(blank=True, null=True)
    contract_start_date = models.DateField(blank=True, null=True)
    contract_end_date = models.DateField(blank=True, null=True)
