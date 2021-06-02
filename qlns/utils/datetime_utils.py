from datetime import timedelta, date

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


def to_date_string(dt):
    if isinstance(dt, date):
        return dt.strftime('%d/%m/%Y')
    local_date = timezone.localtime(dt)
    return local_date.strftime('%d/%m/%Y')


CRON_WEEKDAYS = {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 0, }
PY_WEEKDAYS = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6, }


def to_cron_weekday(py_weekday):
    if py_weekday < 6:
        return py_weekday + 1
    else:
        return 0
