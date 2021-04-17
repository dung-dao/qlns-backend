from django.db import models


class EmployeeEducation(models.Model):
    owner = models.ForeignKey(
        to='Employee', on_delete=models.CASCADE, related_name='education')
    education_level = models.ForeignKey(to='EducationLevel', on_delete=models.CASCADE)
    institute = models.CharField(max_length=255, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    GPA = models.FloatField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
