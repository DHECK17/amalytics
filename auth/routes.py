from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_login.utils import login_required
from passlib.hash import bcrypt

from .forms import LoginForm, SignUpForm
from .models import Accounts, User

auth = Blueprint("auth", __name__, template_folder="templates", url_prefix="/auth")


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user_exists = Accounts.get(username)
        if user_exists is not None:
            flash("Username taken")
            return redirect(url_for("homepage"))
        print(Accounts.create(username, bcrypt.hash(password)))
        login_user(User(username))
        flash(f"Account created")
        return redirect(url_for("homepage"))
    if current_user.is_authenticated:
        return redirect(url_for("sites.new_site"))
    return render_template("registration/signup.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        account = Accounts.get(username)
        if account is None:
            flash("Account does not exist")
            return redirect(url_for("auth.login"))
        account = account[0]
        if not bcrypt.verify(password, account["password"]):
            flash("Wrong password")
        else:
            login_user(User(account["username"]))
            flash(f"Logged in as {username}")
            return redirect(url_for("sites.new_site"))
        return redirect(url_for("auth.login"))
    if current_user.is_authenticated:
        return redirect(url_for("sites.new_site"))
    return render_template("registration/login.html", form=form)


@login_required
@auth.get("/logout")
def logout():
    logout_user()
    flash("Logout successful")
    return redirect(url_for("homepage"))
