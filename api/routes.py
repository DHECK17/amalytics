import json
import threading
from datetime import datetime
from hashlib import sha256
from os import getenv

import app
import requests
from flask import Blueprint, abort, jsonify, request
from flask_cors import CORS
from flask_login import login_required
from sites.models import Website
from user_agents import parse

from .models import Click
from .utils import get_browser_count, get_data_for_a_period, referrer_count

api = Blueprint("api", __name__, url_prefix="/api")
CORS(api, resources={r"/api/click": {"origins": "*", "headers": "Content-Type"}})


def get_country_from_ip(ip: str) -> str:
    endpoint = f"http://ip-api.com/json/{ip}"
    result = requests.get(endpoint).json()
    location = {
        "country": result.get("countryCode"),
        "location": {
            "latitude": result.get("lat"),
            "longitude": result.get("lon"),
        },
    }
    return location


def hash_sha256(payload: str) -> str:
    m = sha256()
    m.update(payload.encode())
    return m.hexdigest()


def get_location_and_create_click(ip: str, data: dict):
    extraas = {
        "ip": ip,
        "location": get_country_from_ip(ip),
        "created_at": datetime.now().date().isoformat(),
    }
    if data.get("outerWidth") >= 1000:
        data["device"] = "Desktop"
    else:
        data["device"] = "Mobile"

    try:
        del data["outerWidth"]
    except KeyError:
        pass

    # sanitize page url
    schemes = ["https://", "http://", "www."]
    domain: str = data.get("domain")
    page_url: str = data.get("pageURL")
    for scheme in schemes:
        page_url = page_url.removeprefix(scheme)
    page_url = page_url.removeprefix(domain)
    data["pageURL"] = page_url

    data.update(extraas)
    Click.create(data)


@api.post("/click")
def click():
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    data: dict = json.loads(request.data)
    page = data.get("pageURL")

    hashable_string = f"{ip}-{user_agent}-{page}"
    user_hash = hash_sha256(hashable_string)

    if app.redis_client.get(user_hash) is None:
        if ip == "127.0.0.1":
            abort(400, "Local addresses not supported")

        domain_exist = Website.get_website(data.get("domain"))
        if domain_exist is None or domain_exist == []:
            abort(400, "Domain not registered")

        browser, os = None, None

        if user_agent is not None:
            user_agent = parse(user_agent)
            browser = user_agent.browser.family
            os = user_agent.os.family

        data.update(browser=browser, os=os)
        app.redis_client.set(user_hash, "+", getenv("HASH_EXPIRY"))

        # run in background
        threading.Thread(
            target=get_location_and_create_click,
            args=(
                ip,
                data,
            ),
        ).start()
    return jsonify(hello="world")


@api.get("/<path:website>/analytics")
@login_required
def analytics_data(website: str):
    data = Click.get_click_data(website)
    print(website)
    if data is None:
        return jsonify(None)

    result = dict()
    result.update(referrer=referrer_count(data))
    result.update(click_count=get_data_for_a_period(data))
    result.update(browser_count=get_browser_count(data))

    return jsonify(result)
