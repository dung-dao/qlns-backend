from datetime import timedelta

from django.db import models
from django.utils import timezone

from qlns.apps.core import models as core_models


class Period(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        unique_together = [['start_date', 'end_date']]

    @staticmethod
    def get_or_create(seed_datetime):
        # Get app config
        app_config = core_models.ApplicationConfig.objects.first()

        # Get period if available
        start_date = timezone.localtime(seed_datetime) \
            .replace(day=app_config.monthly_start_date,
                     hour=0, minute=0, second=0, microsecond=0)

        end_date = timezone.localtime(seed_datetime) \
            .replace(day=app_config.monthly_start_date, month=start_date.month + 1,
                     hour=0, minute=0, second=0, microsecond=0)
        end_date -= timedelta(microseconds=1)

        (period, created) = Period.objects.get_or_create(start_date=start_date, end_date=end_date)
        return period

    @staticmethod
    def get_period(seed_datetime):
        app_config = core_models.ApplicationConfig.objects.first()
        start_date = timezone.localtime(seed_datetime) \
            .replace(day=app_config.monthly_start_date,
                     hour=0, minute=0, second=0, microsecond=0)

        end_date = timezone.localtime(seed_datetime) \
            .replace(day=app_config.monthly_start_date, month=start_date.month + 1,
                     hour=0, minute=0, second=0, microsecond=0)
        end_date -= timedelta(microseconds=1)
        period = Period.objects.filter(start_date=start_date, end_date=end_date).first()
        return period
