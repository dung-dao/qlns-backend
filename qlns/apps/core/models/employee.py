from django.db import models
from django.contrib.auth.models import User
from .country import Country
import uuid
import os


def upload_to(instance, filename):
    _, file_extension = os.path.splitext('/'+filename)
    return 'avatars/' + str(uuid.uuid4()) + file_extension


class Employee(models.Model):
    def __str__(self):
        return (self.first_name + " " + self.last_name).strip()

    # Enum
    class Gender(models.TextChoices):
        Male = 'Male'
        Female = 'Female'
        Other = 'Other'

    class MaritalStatus(models.TextChoices):
        Single = "Single"
        Married = "Married"
        Divorced = 'Divorced'
        Seperated = 'Seperated'
        Widowed = 'Widowed'
        Other = 'Other'

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()

    gender = models.CharField(
        max_length=10, choices=Gender.choices, blank=True)
    marital_status = models.CharField(
        max_length=10, choices=MaritalStatus.choices, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    personal_tax_id = models.CharField(max_length=50, blank=True)
    nationality = models.ForeignKey(
        to='Country', on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=20, blank=True)
    social_insurance = models.CharField(max_length=20, blank=True)
    health_insurance = models.CharField(max_length=20, blank=True)

    avatar = models.ImageField(
        upload_to=upload_to, default='avatars/default_avatar.svg')

    # related data
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def get_role(self):
        if self.user.is_superuser:
            return "superuser".upper()
        g = self.user.groups.first()
        if g is not None:
            return g.name.upper()
        else:
            return "N/A"
