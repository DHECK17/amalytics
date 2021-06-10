from flask import Blueprint, redirect, render_template, request, url_for
from flask.helpers import flash
from flask_login import current_user, login_required

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
    return render_template("sites/site.html", website=website)
