from django.db import models


class SalaryTemplateField(models.Model):
    class Meta:
        default_permissions = ()

    class Datatype(models.TextChoices):
        Number = 'Number'
        Currency = 'Currency'
        Text = 'Text'

    class SalaryFieldType(models.TextChoices):
        SystemField = 'System Field'
        Formula = 'Formula'

    template = models.ForeignKey(to='SalaryTemplate', on_delete=models.CASCADE, related_name='fields')
    index = models.IntegerField()
    type = models.CharField(max_length=50, choices=SalaryFieldType.choices)
    datatype = models.CharField(max_length=20, choices=Datatype.choices)
    code_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    define = models.CharField(max_length=1024, null=True, blank=True)
