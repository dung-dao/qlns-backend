from django.db import models


class ContactInfo(models.Model):
    owner = models.OneToOneField(
        to='Employee', on_delete=models.CASCADE, related_name='contact_info')

    address = models.CharField(max_length=255)
    country = models.ForeignKey(
        to='Country', on_delete=models.SET_NULL, null=True)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
