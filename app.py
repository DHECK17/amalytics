import os

from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from api.routes import api
from auth.models import Accounts, User
from auth.routes import auth
from sites.routes import sites

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["CORS_HEADERS"] = "application/json"
app.register_blueprint(auth)
app.register_blueprint(sites)
app.register_blueprint(api)

login_manager = LoginManager()
csrf_protect = CSRFProtect()

login_manager.init_app(app)
csrf_protect.init_app(app)
csrf_protect.exempt("api.routes.click")


@login_manager.user_loader
def load_user(user_id):
    user = Accounts.get(user_id)[0]["username"]
    return User(user)


@app.get("/")
def homepage():
    return render_template("home.html")


@app.get("/amalytics.js")
def serve_script():
    return send_from_directory("./script", "amalytics.js")


if __name__ == "__main__":
    print(os.environ.get("HARPER_USERNAME"))
    app.run(debug=True, load_dotenv=True)
