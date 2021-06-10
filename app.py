import os

from flask import Flask, render_template, send_from_directory
from flask.helpers import url_for
from flask_login import LoginManager
from flask_redis import FlaskRedis
from flask_wtf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import redirect

from api.routes import api
from auth.forms import SignUpForm
from auth.models import Accounts, User
from auth.routes import auth
from sites.routes import sites

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

app.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))
app.config.update(CORS_HEADERS="application/json")
app.config.update(LOGIN_DISABLED=False)
app.config.update(REDIS_URL="redis://:@redis:6379/0")

app.register_blueprint(auth)
app.register_blueprint(sites)
app.register_blueprint(api)

login_manager = LoginManager()
csrf_protect = CSRFProtect()
redis_client = FlaskRedis()

login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized_user():
    return redirect(url_for("auth.login"))


csrf_protect.init_app(app)
csrf_protect.exempt("api.routes.click")

redis_client.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    user = Accounts.get(user_id)[0]["username"]
    return User(user)


@app.get("/")
def homepage():
    return render_template("home.html", form=SignUpForm())


@app.get("/amalytics.js")
def serve_script():
    return send_from_directory("./script", "amalytics.js")


if __name__ == "__main__":
    app.run(debug=True, load_dotenv=True)
