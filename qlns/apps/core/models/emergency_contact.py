from django.db import models


class EmergencyContact(models.Model):
    owner = models.OneToOneField(
        to='Employee', on_delete=models.CASCADE, related_name='emergency_contact')

    fullname = models.CharField(max_length=150)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
