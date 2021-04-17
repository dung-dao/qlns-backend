from django.db import models


class EmployeeLanguage(models.Model):
    class LanguageSkill(models.TextChoices):
        Reading = 'Reading'
        Speaking = 'Speaking'
        Writing = 'Writing'

    class FluencyLevel(models.TextChoices):
        Poor = 'Poor'
        Basic = 'Basic'
        Good = 'Good'
        MotherTongue = 'Mother Tongue'

    language = models.ForeignKey(to='Language', on_delete=models.CASCADE)
    owner = models.ForeignKey(
        to='Employee', on_delete=models.CASCADE, related_name='languages')
    skill = models.CharField(max_length=20, choices=LanguageSkill.choices)
    fluency_level = models.CharField(max_length=20, choices=FluencyLevel.choices)
    note = models.TextField(blank=True)
