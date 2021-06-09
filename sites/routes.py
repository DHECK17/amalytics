from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from .forms import WebsiteForm
from .models import Website

sites = Blueprint("sites", __name__, url_prefix="/sites")


@login_required
@sites.route("/", methods=["GET", "POST"])
def new_site():
    form = WebsiteForm()
    username = current_user.id
    if request.method == "POST" and form.validate_on_submit():
        website = form.name.data
        Website.create(website, username)
    websites = Website.get_all_websites(username)
    return render_template("sites/new_site.html", form=form, websites=websites)


@login_required
@sites.route("/<path:website>", methods=["GET", "POST"])
def site(website: str):
    return render_template("sites/site.html", website=website)
