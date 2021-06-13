from collections import Counter
from datetime import datetime, timedelta


def get_referrer_country_pagevisit_browser_device(data: dict):
    referrers = []
    countries = []
    visits = []
    browsers = []
    devices = []

    for i in data:
        referrers.append(i.get("referrer"))
        countries.append(i.get("location").get("country"))
        visits.append(i.get("pageURL"))
        browsers.append(i.get("browser"))
        devices.append(i.get("device"))

    return (
        Counter(referrers),
        Counter(countries),
        Counter(visits),
        Counter(browsers),
        Counter(devices),
    )


def referrer_count(data: dict):
    referrers = []
    for i in data:
        referrers.append(i.get("referrer"))
    return Counter(referrers)


def get_country(data: dict):
    countries = []
    for i in data:
        countries.append(i.get("location").get("country"))
    return Counter(countries)


def page_visit_count(data: dict):
    visits = []
    for i in data:
        visits.append(i.get("pageURL"))
    return Counter(visits)


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
