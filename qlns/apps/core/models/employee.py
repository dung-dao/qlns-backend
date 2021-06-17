import os
import pickle
import uuid

import face_recognition
import numpy as np
from django.contrib.auth.models import User
from django.db import models

from ...attendance.models import EmployeeSchedule


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

    face_model_path = models.CharField(max_length=1000, null=True)

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
            return "N/A"

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
        if self.face_model_path is None:
            return False

        pic = np.array(image.convert('RGB'))
        faces = face_recognition.face_locations(pic, model='cnn')

        if len(faces) != 1:
            return False
        unknown_face_enc = face_recognition.face_encodings(pic)[0]
        employee_face_enc = pickle.load(open(self.face_model_path, 'rb'))
        return face_recognition.compare_faces([employee_face_enc], unknown_face_enc, tolerance=0.4)[0]

    def update_face_model(self):
        if self.avatar == self.avatar.field.default:
            return

        img_path = self.avatar.path
        face_img = face_recognition.load_image_file(img_path)
        faces = face_recognition.face_locations(face_img)
        if len(faces) != 1:
            return

        face_enc = face_recognition.face_encodings(face_img)[0]
        filename = self.face_model_path if self.face_model_path is not None \
            else './private_files/trained_models/' + str(uuid.uuid4()) + '.sav'
        pickle.dump(face_enc, open(filename, 'wb'))
        self.face_model_path = filename
        self.save()
