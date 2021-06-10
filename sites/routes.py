from api.models import Click
from api.utils import (
    get_browser_count,
    get_data_for_a_period,
    get_device_count,
    referrer_count,
)
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
        for scheme in ["https://", "http://", "www."]:
            if website.startswith(scheme):
                website = website.removeprefix(scheme)
        Website.create(website, username)
    websites = Website.get_all_websites(username)
    return render_template("sites/new_site.html", form=form, websites=websites)


@sites.route("/<path:website>", methods=["GET", "POST"])
@login_required
def site(website: str):
    data = Click.get_click_data(website)
    if data is None:
        return jsonify(None)

    click_count = get_data_for_a_period(data)
    browser_count = get_browser_count(data)
    device_count = get_device_count(data)

    result = dict()
    result.update(referrer=referrer_count(data))
    result.update(click_count=click_count)
    result.update(browser_count=browser_count)
    result.update(device_count=device_count)

    # Build chart of the browser used
    class BrowserChart(BaseChart):
        type = ChartType.Pie

        class data:
            label = "Browser type used"
            data = list(browser_count.values())
            backgroundColor = Color.Palette(Color.Green, n=len(data), generator="hue")

        class labels:
            grouped = list(browser_count.keys())

    # Build chart of the browser used
    class DeviceChart(BaseChart):
        type = ChartType.Pie

        class data:
            label = "Device type used"
            data = list(device_count.values())
            backgroundColor = Color.Palette(Color.Blue, n=len(data), generator="hue")

        class labels:
            grouped = list(device_count.keys())

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
    )
