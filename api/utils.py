from collections import Counter
from datetime import datetime, timedelta


def referrer_count(data: dict):
    referrers = []
    for i in data:
        referrers.append(i.get("referrer"))
    return Counter(referrers)


def get_data_for_a_period(data: dict) -> dict:
    periods = [30, 7, 1]
    result = dict()
    for period in periods:
        current_date = (datetime.now() + timedelta(days=-period)).date().isoformat()
        dates = []
        for i in data:
            date = i.get("created_at")
            if date > current_date:
                dates.append(date)
        result.update({period: Counter(dates)})
    return result


def get_browser_count(data: dict):
    browsers = []
    for item in data:
        browsers.append(item.get("browser"))
    return Counter(browsers)


def get_device_count(data: dict):
    devices = []
    for item in data:
        devices.append(item.get("device"))
    return Counter(devices)
