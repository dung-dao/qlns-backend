import os
import uuid

from django.db import models


def upload_to(instance, filename):
    _, file_extension = os.path.splitext('/' + filename)
    return 'azure_face_images/' + str(uuid.uuid4()) + file_extension


class EmployeeFace(models.Model):
    class Meta:
        default_permissions = ('view', 'add', 'delete',)

    owner = models.ForeignKey(to='core.Employee', on_delete=models.CASCADE, related_name='Faces')
    azure_face_id = models.CharField(max_length=100)
    image = models.ImageField(upload_to=upload_to)
    timestamp = models.DateTimeField(auto_now_add=True)
