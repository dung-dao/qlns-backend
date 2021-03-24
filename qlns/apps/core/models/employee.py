from django.db import models
from django.contrib.auth.models import User
from .country import Country


class Employee(models.Model):
    def __str__(self):
        return (self.first_name + " " + self.last_name).strip()

    # Enum
    class Gender(models.TextChoices):
        Male = 'Male'
        Female = 'Female'

    class MaritalStatus(models.TextChoices):
        Single = "Single"
        Married = "Married"

    # Fields
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10, choices=Gender.choices)
    marital_status = models.CharField(
        max_length=10, choices=MaritalStatus.choices)

    street = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)

    home_telephone = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=100, blank=True)

    work_telephone = models.CharField(max_length=100, blank=True)
    work_email = models.CharField(max_length=100, blank=True)

    # related data
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.ForeignKey(
        Country, related_name='employees', null=True, on_delete=models.SET_NULL)
    supervisor = models.ForeignKey(
        'self', related_name='employee', null=True, on_delete=models.SET_NULL)
