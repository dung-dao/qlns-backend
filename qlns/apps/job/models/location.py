from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=150, unique=True)
    country = models.ForeignKey(to='core.Country', on_delete=models.PROTECT)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    zipcode = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)

    radius = models.FloatField(default=100)
    allow_outside = models.BooleanField(default=True)
    accurate_address = models.CharField(max_length=1000, blank=True)

    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)