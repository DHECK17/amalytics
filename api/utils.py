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


# def get_data_for_a_period(data: dict) -> dict:
#     periods = [30, 7, 1]
#     result = dict()
#     for period in periods:
#         current_date = (datetime.now() + timedelta(days=-period)).date().isoformat()
#         dates = []
#         for i in data:
#             date = i.get("created_at")
#             if date > current_date:
#                 dates.append(date)
#         result.update({period: Counter(dates)})
#     return result


def get_data_for_a_period(data: dict) -> dict:
    result = dict()
    date_x = lambda x: (datetime.now() + timedelta(days=-x)).date().isoformat()
    date_30, date_7, date_1 = date_x(30), date_x(7), date_x(1)

    dates_30, dates_7, dates_1 = [], [], []

    for i in data:
        date = i.get("created_at")
        if date > date_30:
            dates_30.append(date)

        if date > date_7:
            dates_7.append(date)

        if date > date_1:
            dates_1.append(date)

    result.update(
        {
            30: Counter(dates_30),
            7: Counter(dates_7),
            1: Counter(dates_1),
        }
    )

    return result
