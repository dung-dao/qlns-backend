from django.db import models


class Job(models.Model):
    owner = models.ForeignKey(
        to='core.Employee', on_delete=models.CASCADE, related_name='job_history')
    job_title = models.ForeignKey(to='JobTitle', on_delete=models.PROTECT, related_name='jobs')
    location = models.ForeignKey(to='Location', on_delete=models.PROTECT, related_name='jobs')
    employment_status = models.ForeignKey(to='EmploymentStatus', on_delete=models.PROTECT)
    event = models.ForeignKey(to='JobEvent', on_delete=models.PROTECT)

    work_shift = models.ForeignKey(to='WorkShift', on_delete=models.SET_NULL, null=True, related_name='jobs')
    department = models.ForeignKey(to='core.Department', on_delete=models.SET_NULL, null=True, related_name='jobs')
    probation_start_date = models.DateField(blank=True, null=True)
    probation_end_date = models.DateField(blank=True, null=True)
    contract_start_date = models.DateField(blank=True, null=True)
    contract_end_date = models.DateField(blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)
