from datetime import date

from django.utils import timezone


def PIT_VN(thu_nhap_tinh_thue):
    if thu_nhap_tinh_thue <= 5000000:
        return 5 / 100 * thu_nhap_tinh_thue
    elif thu_nhap_tinh_thue <= 10000000:
        return 10 / 100 * thu_nhap_tinh_thue - 250000
    elif thu_nhap_tinh_thue <= 18000000:
        return 15 / 100 * thu_nhap_tinh_thue - 750000
    elif thu_nhap_tinh_thue <= 32000000:
        return 20 / 100 * thu_nhap_tinh_thue - 1650000
    elif thu_nhap_tinh_thue <= 52000000:
        return 25 / 100 * thu_nhap_tinh_thue - 3250000
    elif thu_nhap_tinh_thue <= 80000000:
        return 30 / 100 * thu_nhap_tinh_thue - 5850000
    else:
        return 35 / 100 * thu_nhap_tinh_thue - 9850000


def convert_to_datestring(dt):
    if isinstance(dt, date):
        return dt.strftime('%d/%m/%Y')
    local_date = timezone.localtime(dt)
    return local_date.strftime('%d/%m/%Y')
