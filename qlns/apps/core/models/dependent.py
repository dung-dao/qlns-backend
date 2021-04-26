from django.db import models


class Dependent(models.Model):
    owner = models.ForeignKey(to='Employee', on_delete=models.CASCADE, related_name='Dependents')

    class Gender(models.TextChoices):
        Male = 'Male'
        Female = 'Female'
        Other = 'Other'

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateTimeField(blank=True, null=True)
    gender = models.CharField(max_length=50, choices=Gender.choices, blank=True, null=True)
    relationship = models.CharField(max_length=255, blank=True, null=True)
    nationality = models.ForeignKey(to='Country', on_delete=models.SET_NULL, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    personal_id = models.CharField(max_length=20, blank=True, null=True)
    personal_tax_id = models.CharField(max_length=30, blank=True, null=True)

    effective_start_date = models.DateTimeField(null=True)
    effective_end_date = models.DateTimeField(null=True)
