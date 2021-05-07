from datetime import datetime

import pytz

MIN_UTC_DATETIME = datetime.min.replace(tzinfo=pytz.utc)
MAX_UTC_DATETIME = datetime.max.replace(tzinfo=pytz.utc)
