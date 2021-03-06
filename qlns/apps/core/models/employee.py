import os
import uuid

from django.contrib.auth.models import User
from django.db import models

from ...attendance.models import EmployeeSchedule
from ...attendance.services.face_services import verify, create_person


def upload_to(instance, filename):
    _, file_extension = os.path.splitext('/' + filename)
    return 'avatars/' + str(uuid.uuid4()) + file_extension


class Employee(models.Model):
    class Meta:
        default_permissions = ('add', 'change', 'view')
        permissions = (
            ('can_set_role_employee', 'Can change employee role'),
            ('can_set_password_employee', 'Can change employee password'),
            ('can_change_avatar_employee', 'Can change employee avatar (also use for face identity)'),
        )

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

    recognition_id = models.CharField(max_length=100, null=True)

    # related data
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    current_job = models.ForeignKey(to='job.Job', on_delete=models.SET_NULL, null=True)

    @property
    def full_name(self):
        return (self.first_name + " " + self.last_name).strip()

    def get_role(self):
        if self.user.is_superuser:
            return "superuser".upper()
        g = self.user.groups.first()
        if g is not None:
            return g.name.upper()
        else:
            return "USER"

    def get_permissions(self):
        permissions = self.user.get_all_permissions()
        return permissions

    def get_current_schedule(self):
        em_schedule = EmployeeSchedule.objects.filter(owner=self.pk)
        em_schedule = em_schedule.first()
        return None if em_schedule is None else em_schedule.schedule

    def get_job_location(self):
        current_job = self.job_history.order_by('-timestamp').first()
        return None if current_job is None else current_job.location

    def get_employment_status(self):
        current_job = self.job_history.order_by('-timestamp').first()
        return current_job.employment_status.name if current_job is not None else "N/A"

    def get_current_job(self):
        return self.job_history.order_by('-timestamp').first()

    def is_working(self):
        if self.current_job is not None and hasattr(self.current_job, 'termination'):
            return False
        return True

    def get_status(self):
        if self.current_job is not None:
            if hasattr(self.current_job, 'termination'):
                return "Terminated"
            else:
                return "Working"
        elif self.current_job is None:
            return "NewHired"

    def identify_image(self, image):
        if self.recognition_id is None:
            self.recognition_id = create_person(self.full_name)
            self.save()

        return verify(self.recognition_id, image)

    def get_username(self):
        return self.user.username
