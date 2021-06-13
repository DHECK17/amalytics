from datetime import datetime, timedelta
from urllib.parse import urlparse

from api.utils import (
    get_browser_count,
    get_data_for_a_period,
    get_device_count,
    get_referrer_country_pagevisit_browser_device,
    page_visit_count,
    referrer_count,
)
from db import db
from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask.helpers import flash
from flask_login import current_user, login_required
from pychartjs import BaseChart, ChartType, Color

from .forms import WebsiteForm
from .models import Website

sites = Blueprint("sites", __name__, url_prefix="/sites")


@sites.route("/", methods=["GET", "POST"])
@login_required
def new_site():
    form = WebsiteForm()
    username = current_user.id
    if request.method == "POST" and form.validate_on_submit():
        website = form.name.data
        website_exists = Website.get_website(website)
        if website_exists is not None:
            flash("Website already added to amalytics")
            return redirect(url_for("sites.new_site"))
        if website[-1] == "/":
            website = website[:-1]
        website = urlparse(website).netloc
        if website == "":
            flash("Please enter a valid website")
            return redirect(url_for("sites.new_site"))
        Website.create(website, username)
    websites = Website.get_all_websites(username)
    return render_template("sites/new_site.html", form=form, websites=websites)


@sites.route("/<path:website>", methods=["GET", "POST"])
@login_required
def site(website: str):
    ts = (datetime.now() + timedelta(days=-30)).timestamp()
    data = db.sql(
        f"SELECT * FROM amalytics.clicks WHERE __createdtime__ > {ts} AND domain='{website}'"
    )
    if data is None:
        return jsonify(None)

    click_count = get_data_for_a_period(data)

    (
        referrer,
        countries,
        visits,
        browser_count,
        device_count,
    ) = get_referrer_country_pagevisit_browser_device(data)

    try:
        del referrer[""]
    except KeyError:
        pass

    result = dict()

    # Build chart for referrer count
    class ReferrerChart(BaseChart):
        type = ChartType.HorizontalBar

        class data:
            label = "Referrers"
            data = list(referrer.values())
            backgroundColor = Color.Palette(Color.Magenta, n=len(data), generator="hue")

        class labels:
            grouped = list(referrer.keys())

    # Build chart for click count
    class ClickChart(BaseChart):
        type = ChartType.Line

        class data:
            label = "Views"
            data = list(click_count[30].values())
            backgroundColor = Color.Cyan

        class labels:
            grouped = list(click_count[30].keys())

        class options:
            legend = {
                "labels": {"fontColor": "white"},
            }

    # Build chart for the browser used
    class BrowserChart(BaseChart):
        type = ChartType.Pie

        class data:
            label = "Browser type used"
            data = list(browser_count.values())
            backgroundColor = Color.Palette(Color.Green, n=len(data), generator="hue")

        class labels:
            grouped = list(browser_count.keys())

    # Build chart for the device used
    class DeviceChart(BaseChart):
        type = ChartType.Pie

        class data:
            label = "Device type used"
            data = list(device_count.values())
            backgroundColor = Color.Palette(Color.Blue, n=len(data), generator="hue")

        class labels:
            grouped = list(device_count.keys())

    print(visits.values())

    # Build chart for page visited
    class PageChart(BaseChart):
        type = ChartType.HorizontalBar

        class data:
            label = "Page visited"
            data = list(visits.values())
            backgroundColor = Color.Palette(Color.Cyan, n=len(data), generator="hue")

        class labels:
            grouped = list(visits.keys())

    # Build chart for page visited
    class CountryChart(BaseChart):
        type = ChartType.HorizontalBar

        class data:
            label = "Views"
            data = list(countries.values())
            backgroundColor = Color.Palette(Color.Apricot, n=len(data), generator="hue")

        class labels:
            grouped = list(countries.keys())

    total_clicks = dict()

    for i, v in click_count.items():
        total_clicks[i] = sum(v.values())

    result.update(total_clicks=total_clicks)

    return render_template(
        "sites/site.html",
        website=website,
        data=result,
        browserDataChart=BrowserChart().get(),
        deviceDataChart=DeviceChart().get(),
        clickChart=ClickChart().get(),
        referrerChart=ReferrerChart().get(),
        pageChart=PageChart().get(),
        countryChart=CountryChart().get(),
    )
