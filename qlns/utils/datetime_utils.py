from datetime import timedelta

import pytz
from dateutil.parser import isoparse
from django.utils import timezone


def parse_iso_datetime(date_str, default=None):
    try:
        dt = isoparse(date_str)
        if timezone.is_naive(dt):
            dt = dt.replace(tzinfo=pytz.utc)
        return dt
    except ValueError:
        return default
    except TypeError:
        return default


def local_now():
    return timezone.localtime(timezone.now())


def get_next_date(dt):
    current_moment = timezone.localtime(dt)
    next_day_first_moment = (current_moment + timedelta(days=1)) \
        .replace(hour=0, minute=0, second=0, microsecond=0)
    return next_day_first_moment
